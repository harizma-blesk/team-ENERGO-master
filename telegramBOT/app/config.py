"""
Configuration for the Telegram Bot.
Loads settings from environment variables using Pydantic.
"""

import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings


# Load .env file from the project root (parent of app directory)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class LocationOption(BaseModel):
    """Represents a location option (building/office)."""
    id: str
    name: str
    floors: list[int]


class Settings(BaseSettings):
    """Bot configuration loaded from environment variables."""
    
    # Telegram
    telegram_bot_token: SecretStr = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    
    # PHP API
    php_base_url: str = Field(default="http://localhost:3333", alias="PHP_BASE_URL")
    php_api_paths: dict[str, str] = Field(default_factory=dict, alias="PHP_API_PATHS")
    php_auth_scheme: str = Field(default="none", alias="PHP_AUTH_SCHEME")
    php_auth_secret: str = Field(default="", alias="PHP_AUTH_SECRET")
    php_api_key_header: str = Field(default="X-API-Key", alias="PHP_API_KEY_HEADER")
  
    
    # Request settings
    request_timeout_seconds: int = Field(default=8, alias="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, alias="MAX_RETRIES")
    retry_backoff_base: float = Field(default=0.6, alias="RETRY_BACKOFF_BASE")
    
    # Storage
    storage_path: str = Field(default="data/users.json", alias="STORAGE_PATH")
    log_path: str = Field(default="logs/bot.log", alias="LOG_PATH")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Locations and filters
    locations_list: list[LocationOption] = Field(default_factory=list, alias="LOCATIONS_LIST")
    search_filters: dict[str, Any] = Field(default_factory=dict, alias="SEARCH_FILTERS")
    admin_telegram_ids: list[int] = Field(default_factory=list, alias="ADMIN_TELEGRAM_IDS")
    
    model_config = {
        "env_file": str(env_path),
        "case_sensitive": False,
    }
    
    def __init__(self, **data):
        # Parse LOCATIONS_LIST from JSON string if needed
        if "LOCATIONS_LIST" in data and isinstance(data["LOCATIONS_LIST"], str):
            try:
                data["LOCATIONS_LIST"] = json.loads(data["LOCATIONS_LIST"])
            except (json.JSONDecodeError, TypeError):
                data["LOCATIONS_LIST"] = []
        
        # Parse SEARCH_FILTERS from JSON string if needed
        if "SEARCH_FILTERS" in data and isinstance(data["SEARCH_FILTERS"], str):
            try:
                data["SEARCH_FILTERS"] = json.loads(data["SEARCH_FILTERS"])
            except (json.JSONDecodeError, TypeError):
                data["SEARCH_FILTERS"] = {}
        
        # Parse ADMIN_TELEGRAM_IDS - can be JSON array or comma-separated
        if "ADMIN_TELEGRAM_IDS" in data and isinstance(data["ADMIN_TELEGRAM_IDS"], str):
            try:
                data["ADMIN_TELEGRAM_IDS"] = json.loads(data["ADMIN_TELEGRAM_IDS"])
            except (json.JSONDecodeError, TypeError):
                # Try parsing as comma-separated values
                try:
                    data["ADMIN_TELEGRAM_IDS"] = [
                        int(x.strip()) for x in data["ADMIN_TELEGRAM_IDS"].split(",") if x.strip()
                    ]
                except ValueError:
                    data["ADMIN_TELEGRAM_IDS"] = []
        
        # Parse PHP_API_PATHS from JSON string if needed
        if "PHP_API_PATHS" in data and isinstance(data["PHP_API_PATHS"], str):
            try:
                data["PHP_API_PATHS"] = json.loads(data["PHP_API_PATHS"])
            except (json.JSONDecodeError, TypeError):
                data["PHP_API_PATHS"] = {}
        
        super().__init__(**data)

    def get_location(self, location_id: str) -> LocationOption | None:
        """Get location by ID from locations_list."""
        for loc in self.locations_list:
            if loc.id == location_id:
                return loc
        return None

    @property
    def bridge_path(self) -> str:
        """Get the bridge API path."""
        return self.php_api_paths.get("bridge", "/api/bridge")

    @property
    def cancel_path(self) -> str:
        """Get the cancel API path."""
        return self.php_api_paths.get("cancel", "/api/cancel")


def get_settings() -> Settings:
    """Get the bot settings from environment variables."""
    return Settings()

def build_locations_from_auditories(auditories: list[dict]) -> list[LocationOption]:
    corpus_floors: dict[str, set[int]] = {}

    for aud in auditories:
        corpus = aud.get("corpus")
        floor = aud.get("floor")  # ← берём из поля floor напрямую
        if not corpus or floor is None:
            continue
        if corpus not in corpus_floors:
            corpus_floors[corpus] = set()
        corpus_floors[corpus].add(int(floor))

    corpus_to_id = {"А": "corp_a", "Б": "corp_b", "Д": "corp_d"}

    locations = []
    for corpus, floors in sorted(corpus_floors.items()):
        locations.append(LocationOption(
            id=corpus_to_id.get(corpus, corpus.lower()),
            name=f"Корпус {corpus}",
            floors=sorted(floors),
        ))
    return locations