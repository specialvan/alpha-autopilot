from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "alpha-autopilot api"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    benchmark_model: str | None = None
    benchmark_api_key: str | None = None
    plotpilot_report_api_url: str | None = None
    plotpilot_report_api_key: str | None = None
    plotpilot_report_api_timeout_seconds: float = 8.0
    plotpilot_report_api_max_attempts: int = 3
    plotpilot_report_api_backoff_seconds: float = 0.2
    v4_genre_auto_min_samples: int = 4
    v4_genre_auto_decay: float = 0.9
    v4_genre_auto_bias_limit: float = 0.12
    v4_genre_auto_max_volatility: float = 0.58
    v4_genre_auto_max_signal_divergence: float = 0.32
    v4_genre_auto_extreme_signal: float = 0.82
    v4_genre_auto_extreme_min_samples: int = 10
    v4_genre_auto_reversal_divergence_min: float = 0.24
    v4_genre_guard_overrides_json: str | None = None
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
