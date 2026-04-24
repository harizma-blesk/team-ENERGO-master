from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Any

from pydantic import BaseModel, Field

CLASS_START_TIMES = [
    time(8, 0),
    time(9, 30),
    time(11, 0),
    time(12, 40),
    time(14, 10),
    time(15, 30),
]

GRACE_PERIOD_MINUTES = 10


def find_next_available_slot(
    duration_minutes: int,
    existing_bookings: list[dict] | None = None,
) -> datetime:
    now = datetime.now()
    today = now.date()

    booked_intervals: list[tuple[datetime, datetime]] = []
    for b in (existing_bookings or []):
        try:
            b_start = datetime.combine(today, time.fromisoformat(b["startTime"]))
            b_end   = datetime.combine(today, time.fromisoformat(b["endTime"]))
            booked_intervals.append((b_start, b_end))
        except Exception:
            continue

    booked_intervals.sort(key=lambda x: x[0])

    def shift_past_all(candidate: datetime) -> datetime:
        changed = True
        while changed:
            changed = False
            cand_end = candidate + timedelta(minutes=duration_minutes)
            for b_start, b_end in booked_intervals:
                if candidate < b_end and cand_end > b_start:
                    candidate = b_end
                    changed = True
                    break
        return candidate

    def shift_past_class_times(candidate: datetime) -> datetime:
        changed = True
        while changed:
            changed = False
            for start in CLASS_START_TIMES:
                slot_start = datetime.combine(today, start)
                slot_end   = slot_start + timedelta(minutes=90)
                grace_deadline = slot_start + timedelta(minutes=GRACE_PERIOD_MINUTES)

                if slot_start <= candidate < slot_end:
                    if candidate <= grace_deadline:
                        if candidate + timedelta(minutes=duration_minutes) <= slot_end:
                            return candidate
                    candidate = slot_end
                    changed = True
                    break
        return candidate

    candidate = now
    for _ in range(20):
        new_candidate = shift_past_all(candidate)
        new_candidate = shift_past_class_times(new_candidate)
        if new_candidate == candidate:
            break
        candidate = new_candidate

    return candidate


class FindRoomQuery(BaseModel):
    location_id: str = Field(min_length=1)
    floor: int | None = None
    date: date
    duration_minutes: int = Field(ge=15, le=480)
    min_capacity: int | None = Field(default=None, ge=1, le=500)
    need_projector: bool | None = None
    requested_by: int

    def to_php_payload(self) -> dict[str, Any]:
        filters: dict[str, Any] = {}
        if self.min_capacity is not None:
            filters["min_capacity"] = self.min_capacity
        if self.need_projector is not None:
            filters["need_projector"] = self.need_projector

        start_at = find_next_available_slot(self.duration_minutes)

        payload: dict[str, Any] = {
            "location_id": self.location_id,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "start_at": start_at.isoformat(),
            "requested_by": {"telegram_user_id": self.requested_by},
        }
        if self.floor is not None:
            payload["floor"] = self.floor
        if filters:
            payload["filters"] = filters
        return payload