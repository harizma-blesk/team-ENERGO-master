"""
База данных для Camera Monitor
Использует SQLAlchemy ORM с SQLite
"""

from sqlalchemy import create_engine, String, DateTime, Float, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class Camera(Base):
    """
    Модель камеры

    Хранит информацию о подключенных камерах
    """
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Camera")
    rtsp_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="offline")  # online, offline, error
    last_frame_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Camera(id={self.id}, name='{self.name}', status='{self.status}')>"


class Room(Base):
    """
    Модель кабинета / аудитории
    """
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    building: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    def __repr__(self):
        return f"<Room(id={self.id}, name='{self.name}', building='{self.building}')>"


class CabinetBooking(Base):
    """
    Модель бронирования кабинета

    Хранит информацию о бронированиях аудиторий
    """
    __tablename__ = "cabinet_bookings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cabinet_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    corpus: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    people_count: Mapped[int] = mapped_column(default=0)
    is_temporary: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CabinetBooking(id={self.id}, cabinet='{self.cabinet_id}', corpus='{self.corpus}')>"


class Notification(Base):
    """
    Модель уведомления

    Хранит системные уведомления
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), default="info")  # info, warning, error
    cabinet_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', read={self.is_read})>"


class DetectionLog(Base):
    """
    Модель лога детекции

    Хранит историю детекции людей
    """
    __tablename__ = "detection_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    camera_id: Mapped[int] = mapped_column(index=True)
    people_count: Mapped[int] = mapped_column(nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    cabinet_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<DetectionLog(id={self.id}, camera={self.camera_id}, people={self.people_count})>"


class DatabaseManager:
    """
    Менеджер базы данных

    Управляет подключением к БД и предоставляет методы для работы с данными
    """

    def __init__(self, db_path: str = "camera_monitor.db"):
        """
        Инициализация менеджера БД

        Args:
            db_path: Путь к файлу SQLite БД
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Создаем таблицы
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized at {db_path}")

    def get_session(self) -> Session:
        """Получить сессию БД"""
        return self.SessionLocal()

    def close(self):
        """Закрыть соединение с БД"""
        self.engine.dispose()

    # Camera operations
    def add_camera(self, name: str, rtsp_url: Optional[str] = None, location: Optional[str] = None) -> Camera:
        """Добавить новую камеру"""
        with self.SessionLocal() as session:
            camera = Camera(
                name=name,
                rtsp_url=rtsp_url,
                location=location
            )
            session.add(camera)
            session.commit()
            session.refresh(camera)
            logger.info(f"Added camera: {camera}")
            return camera

    def get_cameras(self) -> List[Camera]:
        """Получить все камеры"""
        with self.SessionLocal() as session:
            return session.query(Camera).all()

    def get_all_rooms(self) -> List[Dict[str, str]]:
        """Получить список всех кабинетов/аудиторий"""
        with self.SessionLocal() as session:
            rooms = session.query(Room).all()
            return [
                {"id": str(room.id), "name": room.name}
                for room in rooms
            ]

    def update_camera_status(self, camera_id: int, status: str):
        """Обновить статус камеры"""
        with self.SessionLocal() as session:
            camera = session.query(Camera).filter(Camera.id == camera_id).first()
            if camera:
                camera.status = status
                camera.updated_at = datetime.now(timezone.utc)
                session.commit()
                logger.info(f"Updated camera {camera_id} status to {status}")

    # Booking operations
    def add_booking(self, cabinet_id: str, corpus: str, start_time: datetime,
                   end_time: datetime, people_count: int = 0) -> CabinetBooking:
        """Добавить бронирование"""
        with self.SessionLocal() as session:
            booking = CabinetBooking(
                cabinet_id=cabinet_id,
                corpus=corpus,
                start_time=start_time,
                end_time=end_time,
                people_count=people_count
            )
            session.add(booking)
            session.commit()
            session.refresh(booking)
            logger.info(f"Added booking: {booking}")
            return booking

    def find_available_cabinets(self, corpus: str, start_time: datetime, end_time: datetime) -> List[str]:
        """Найти свободные кабинеты в указанное время"""
        with self.SessionLocal() as session:
            # Получить занятые кабинеты
            occupied = session.query(CabinetBooking.cabinet_id).filter(
                CabinetBooking.corpus == corpus,
                CabinetBooking.start_time < end_time,
                CabinetBooking.end_time > start_time
            ).distinct().all()

            occupied_ids = [b[0] for b in occupied]

            # TODO: Получить все кабинеты в корпусе и вернуть свободные
            # Пока возвращаем пустой список (нужна таблица cabinets)
            return []

    def initialize_database(self):
        """Создать схемы базы данных, если они не существуют"""
        Base.metadata.create_all(bind=self.engine)

    def clear_temporary_bookings(self) -> int:
        """Очистить временные бронирования"""
        with self.SessionLocal() as session:
            result = session.query(CabinetBooking).filter(
                CabinetBooking.is_temporary == True
            ).delete()
            session.commit()
            logger.info(f"Cleared {result} temporary bookings")
            return result

    # Notification operations
    def add_notification(self, message: str, notification_type: str = "info",
                        cabinet_id: Optional[str] = None) -> Notification:
        """Добавить уведомление"""
        with self.SessionLocal() as session:
            notification = Notification(
                message=message,
                notification_type=notification_type,
                cabinet_id=cabinet_id
            )
            session.add(notification)
            session.commit()
            session.refresh(notification)
            logger.info(f"Added notification: {notification}")
            return notification

    def get_unread_notifications(self) -> List[Notification]:
        """Получить непрочитанные уведомления"""
        with self.SessionLocal() as session:
            return session.query(Notification).filter(
                Notification.is_read == False
            ).order_by(Notification.created_at.desc()).all()

    # Detection logging
    def log_detection(self, camera_id: int, people_count: int, confidence: float,
                     cabinet_id: Optional[str] = None):
        """Залогировать детекцию"""
        with self.SessionLocal() as session:
            log_entry = DetectionLog(
                camera_id=camera_id,
                people_count=people_count,
                confidence=confidence,
                cabinet_id=cabinet_id
            )
            session.add(log_entry)
            session.commit()
            logger.debug(f"Logged detection: camera={camera_id}, people={people_count}")

    def get_detection_stats(self, hours: int = 24) -> dict:
        """Получить статистику детекции за последние N часов"""
        with self.SessionLocal() as session:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

            result = session.query(
                DetectionLog.people_count,
                DetectionLog.confidence
            ).filter(
                DetectionLog.detected_at >= cutoff_time
            ).all()

            if not result:
                return {
                    "total_detections": 0,
                    "avg_people": 0.0,
                    "max_people": 0,
                    "avg_confidence": 0.0
                }

            people_counts = [r[0] for r in result]
            confidences = [r[1] for r in result]

            return {
                "total_detections": len(result),
                "avg_people": sum(people_counts) / len(people_counts),
                "max_people": max(people_counts),
                "avg_confidence": sum(confidences) / len(confidences)
            }