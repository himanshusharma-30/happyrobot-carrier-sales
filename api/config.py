"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    fmcsa_webkey: str
    api_key: str
    database_url: str = "sqlite:///./carrier_sales.db"

    # Negotiation parameters (broker-configurable)
    floor_multiplier: float = 0.92    # 92% of loadboard is our walk-away
    ceiling_multiplier: float = 1.08  # 108% of loadboard is our max
    proximity_accept_pct: float = 0.02  # within 2% of our counter, auto-accept

    # FMCSA caching
    fmcsa_cache_ttl_seconds: int = 600  # 10 min

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8-sig",  # tolerates BOM if present
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()