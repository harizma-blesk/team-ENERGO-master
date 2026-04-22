"""
HTTP синхронизация детекции с Laravel backend.
"""

from __future__ import annotations

import time
from typing import Optional

import requests

from src.core.config import Config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LaravelSyncClient:
    """Отправляет текущее состояние вебки в Laravel API."""

    def __init__(self, base_url: str, auditory_name: str, camera_name: str,
             camera_address: str = '', camera_port: int = 0,
             sync_interval_seconds: int = 2, timeout_seconds: int = 3,
             enabled: bool = True):
        self.enabled = enabled
        self.base_url = base_url.rstrip("/")
        self.auditory_name = auditory_name
        self.camera_name = camera_name
        self.camera_address = camera_address
        self.camera_port = camera_port
        self.sync_interval_seconds = sync_interval_seconds
        self.timeout_seconds = timeout_seconds
        self._last_sync_at = 0.0
        self._last_occupancy: Optional[int] = None

    def can_sync(self) -> bool:
        return self.enabled and bool(self.base_url) and bool(self.auditory_name)

    def sync_detection(self, people_count: int):
        if not self.can_sync():
            return

        occupancy_status = 1 if people_count > 0 else 0
        now = time.time()
        if (
            self._last_occupancy == occupancy_status
            and now - self._last_sync_at < self.sync_interval_seconds
        ):
            return

        payload = {
            "auditory_name": self.auditory_name,
            "name": self.camera_name,
            "stream_address": self.camera_address,
            "stream_port": self.camera_port,
            "is_webcam": 1,
            "occupancy_status": occupancy_status,
            "detected_people": max(0, int(people_count)),
        }

        try:
            response = requests.post(
                f"{self.base_url}/schedule/cameras/detection",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            self._last_sync_at = now
            self._last_occupancy = occupancy_status
        except Exception as e:
            logger.warning(f"Laravel sync failed: {e}")
