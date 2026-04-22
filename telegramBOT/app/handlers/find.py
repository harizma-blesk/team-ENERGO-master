from __future__ import annotations

import logging
from datetime import date, datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError

from app.config import Settings
from app.keyboards.menus import (
    booking_info_keyboard,
    floor_keyboard,
    location_keyboard,
    result_actions_keyboard,
)
from app.models import FindRoomQuery
from app.services.formatter import extract_free_rooms, format_room_details, format_search_result
from app.services.php_client import PhpClient, PhpClientError
from app.storage.user_storage import UserStorage


logger = logging.getLogger(__name__)
router = Router()

BOOKING_DURATION_MINUTES = 80


class FindRoomStates(StatesGroup):
    choosing_location = State()
    choosing_floor = State()


def _format_active_booking(booking: dict) -> str:
    """Format active booking info for display."""
    lines = ["<b>У вас уже есть активная запись:</b>\n"]
    if booking.get("location_name"):
        lines.append(f"📍 Локация: <b>{booking['location_name']}</b>")
    if booking.get("floor") is not None:
        lines.append(f"🏢 Этаж: {booking['floor']}")
    if booking.get("date"):
        lines.append(f"📅 Дата: {booking['date']}")
    if booking.get("available_from"):
        lines.append(f"⏰ Забронировано с: {booking['available_from']}")
    if booking.get("available_until"):
        lines.append(f"⏳ До: {booking['available_until']}")
    if booking.get("booked_at"):
        try:
            booked_at = datetime.fromisoformat(booking["booked_at"])
            lines.append(f"🕐 Запись создана: {booked_at.strftime('%H:%M')}")
        except (ValueError, TypeError):
            pass
    if booking.get("room_info"):
        lines.append(f"\n🚪 Кабинет: <b>{booking['room_info']}</b>")
    lines.append("\nЧтобы сделать новую запись, сначала отмените текущую.")
    return "\n".join(lines)


@router.message(Command("find"))
async def cmd_find(message: Message, state: FSMContext, settings: Settings, user_storage: UserStorage) -> None:
    if not settings.locations_list:
        await message.answer("Список локаций не настроен. Заполните LOCATIONS_LIST в .env.")
        return

    user_id = message.from_user.id if message.from_user else 0

    # Check for active booking
    active_booking = await user_storage.get_active_booking(user_id) if user_id else None
    if active_booking:
        text = _format_active_booking(active_booking)
        await message.answer(text, reply_markup=booking_info_keyboard())
        return

    await state.clear()
    await state.set_state(FindRoomStates.choosing_location)
    default_location = await user_storage.get_default_location(user_id) if user_id else None

    hint = ""
    if default_location:
        location = settings.get_location(default_location)
        if location:
            hint = f"\nТекущая локация по умолчанию: <b>{location.name}</b> ({location.id})."
    await message.answer(
        "Шаг 1/2. Выберите локацию:" + hint,
        reply_markup=location_keyboard(settings.locations_list),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    active_state = await state.get_state()
    if not active_state:
        await message.answer("Активного диалога нет.")
        return
    await state.clear()
    await message.answer("Диалог поиска отменен.")


@router.message(Command("cancelbook"))
async def cmd_cancel_booking(
    message: Message,
    user_storage: UserStorage,
    php_client: PhpClient,
) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not user_id:
        await message.answer("Не удалось определить пользователя.")
        return

    booking = await user_storage.get_active_booking(user_id)
    if not booking:
        await message.answer("У вас нет активной брони.")
        return

    # Call Java API to delete from DB
    cancel_payload = {
        "telegram_user_id": user_id,
        "auditory_name": booking.get("room_info", ""),
        "corpus": booking.get("corpus", ""),
        "start_time": booking.get("available_from", ""),
        "end_time": booking.get("available_until", ""),
    }

    php_error = None
    try:
        result = await php_client.cancel_booking(cancel_payload)
        logger.info("cancel_booking php response: %s", result)
    except PhpClientError as exc:
        logger.error("cancel_booking php error: %s", exc)
        php_error = str(exc)
    except Exception as exc:
        logger.exception("cancel_booking unexpected error")
        php_error = str(exc)

    await user_storage.cancel_booking(user_id)

    if php_error:
        await message.answer(
            "✅ Локальная бронь отменена, но ошибка при удалении из БД.\n"
            f"Детали: {java_error}"
        )
    else:
        await message.answer("✅ Бронь успешно отменена.")


@router.message(Command("mybook"))
async def cmd_my_booking(message: Message, user_storage: UserStorage) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not user_id:
        await message.answer("Не удалось определить пользователя.")
        return
    booking = await user_storage.get_active_booking(user_id)
    if booking:
        text = _format_active_booking(booking)
        await message.answer(text, reply_markup=booking_info_keyboard())
    else:
        await message.answer("У вас нет активной брони.")


async def _ask_floor(message: Message, state: FSMContext, floors: list[int]) -> None:
    await state.set_state(FindRoomStates.choosing_floor)
    await message.answer("Шаг 2/2. Выберите этаж:", reply_markup=floor_keyboard(floors))


@router.callback_query(FindRoomStates.choosing_location, F.data.startswith("findloc:"))
async def callback_find_location(
    callback: CallbackQuery,
    state: FSMContext,
    settings: Settings,
    php_client: PhpClient,
    user_storage: UserStorage,
) -> None:
    location_id = callback.data.split(":", maxsplit=1)[1]
    location = settings.get_location(location_id)
    if location is None:
        await callback.answer("Локация не найдена.", show_alert=True)
        return

    await state.update_data(location_id=location.id, location_name=location.name)
    await callback.answer()
    if not callback.message:
        return
    if location.floors:
        await _ask_floor(callback.message, state, location.floors)
        return
    # No floors — go directly to search
    await state.update_data(floor=None)
    await _execute_search(
        message=callback.message,
        state=state,
        php_client=php_client,
        user_storage=user_storage,
        user_id=callback.from_user.id,
    )


@router.callback_query(FindRoomStates.choosing_floor, F.data.startswith("findfloor:"))
async def callback_find_floor(
    callback: CallbackQuery,
    state: FSMContext,
    php_client: PhpClient,
    user_storage: UserStorage,
) -> None:
    floor_raw = callback.data.split(":", maxsplit=1)[1]
    if floor_raw == "any":
        floor = None
    else:
        try:
            floor = int(floor_raw)
        except ValueError:
            await callback.answer("Некорректный этаж.", show_alert=True)
            return
    await state.update_data(floor=floor)
    await callback.answer()
    if callback.message:
        await _execute_search(
            message=callback.message,
            state=state,
            php_client=php_client,
            user_storage=user_storage,
            user_id=callback.from_user.id,
        )


async def _execute_search(
    *,
    message: Message,
    state: FSMContext,
    php_client: PhpClient,
    user_storage: UserStorage,
    user_id: int,
) -> None:
    data = await state.get_data()
    today = date.today()

    try:
        query = FindRoomQuery(
            location_id=str(data.get("location_id", "")),
            floor=data.get("floor"),
            date=today,
            duration_minutes=BOOKING_DURATION_MINUTES,
            min_capacity=None,
            need_projector=None,
            requested_by=user_id,
        )
    except (ValidationError, ValueError) as exc:
        await state.clear()
        await message.answer(
            "Не удалось собрать корректный запрос. Запустите /find заново.\n"
            f"Детали: {exc}"
        )
        return

    payload = query.to_java_payload()
    logger.info("_execute_search: payload=%s", payload)
    await message.answer(
        f"🔍 Ищу свободный кабинет на сегодня ({today.isoformat()}) "
        f"на {BOOKING_DURATION_MINUTES} мин..."
    )

    try:
        logger.info("_execute_search: calling php_client.bridge(POST)...")
        response = await php_client.bridge(payload=payload)
        logger.info("_execute_search: response=%s", response)
    except PhpClientError as exc:
        await state.clear()
        logger.error(
            "find_request_failed: status_code=%s details=%s",
            exc.status_code,
            exc.details,
        )
        await message.answer(
            "Сервис поиска временно недоступен. Попробуйте позже.\n"
            f"Техническая ошибка: {exc}"
        )
        return
    except Exception as exc:
        await state.clear()
        logger.exception("find_request_unexpected_error")
        await message.answer(
            "Неожиданная ошибка при запросе к Java API.\n"
            f"Детали: {exc}"
        )
        return

    await user_storage.save_last_request(user_id, payload)
    await user_storage.save_last_response(user_id, response)

    # Save active booking
    free_rooms = extract_free_rooms(response)
    room_info = None
    available_from = None
    available_until = None
    corpus = None
    if free_rooms:
        first_room = free_rooms[0]
        room_info = str(
            first_room.get("name")
            or first_room.get("room_name")
            or first_room.get("id")
            or first_room.get("number")
            or "Кабинет"
        )
        available_from = first_room.get("available_from")
        available_until = first_room.get("available_until")
        corpus = first_room.get("location_name")

    booking_data = {
        "location_id": data.get("location_id"),
        "location_name": data.get("location_name"),
        "floor": data.get("floor"),
        "date": today.isoformat(),
        "duration_minutes": BOOKING_DURATION_MINUTES,
        "room_info": room_info,
        "available_from": available_from,
        "available_until": available_until,
        "corpus": corpus,
    }
    await user_storage.save_active_booking(user_id, booking_data)
    await state.clear()

    text = format_search_result(response)
    await message.answer(text)


@router.callback_query(F.data == "cancel_booking")
async def callback_cancel_booking(
    callback: CallbackQuery,
    user_storage: UserStorage,
    php_client: PhpClient,
) -> None:
    user_id = callback.from_user.id
    booking = await user_storage.get_active_booking(user_id)
    await callback.answer()

    if not booking:
        if callback.message:
            await callback.message.answer("У вас нет активной брони.")
        return

    # Call Java API to delete from DB
    cancel_payload = {
        "telegram_user_id": user_id,
        "auditory_name": booking.get("room_info", ""),
        "corpus": booking.get("corpus", ""),
        "start_time": booking.get("available_from", ""),
        "end_time": booking.get("available_until", ""),
    }

    php_error = None
    try:
        result = await php_client.cancel_booking(cancel_payload)
        logger.info("cancel_booking php response: %s", result)
    except PhpClientError as exc:
        logger.error("cancel_booking php error: %s", exc)
        php_error = str(exc)
    except Exception as exc:
        logger.exception("cancel_booking unexpected error")
        php_error = str(exc)

    # Always clear local booking
    await user_storage.cancel_booking(user_id)

    if callback.message:
        if java_error:
            await callback.message.answer(
                "✅ Локальная бронь отменена, но ошибка при удалении из БД.\n"
                f"Детали: {php_error}\n"
                "Используйте /find для новой записи."
            )
        else:
            await callback.message.answer("✅ Бронь успешно отменена. Используйте /find для новой записи.")


@router.callback_query(F.data.startswith("detail:"))
async def callback_room_detail(callback: CallbackQuery, user_storage: UserStorage) -> None:
    payload = await user_storage.get_last_response(callback.from_user.id)
    if payload is None:
        await callback.answer("Нет сохраненного ответа.", show_alert=True)
        return

    raw_index = callback.data.split(":", maxsplit=1)[1]
    if not raw_index.isdigit():
        await callback.answer("Некорректный номер.", show_alert=True)
        return

    details_text = format_room_details(payload, int(raw_index))
    await callback.answer()
    if callback.message:
        await callback.message.answer(details_text)
