from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "alpha-autopilot api"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    benchmark_base_url: str | None = None
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
    v4_observability_latency_p95_ms_threshold: float = 900.0
    v4_observability_error_rate_threshold: float = 0.08
    v4_observability_fallback_rate_threshold: float = 0.35
    v4_alert_remote_enabled: bool = False
    v4_alert_im_webhook_url: str | None = None
    v4_alert_webhook_url: str | None = None
    v4_alert_webhook_timeout_seconds: float = 3.0
    v4_alert_oncall_contacts: str | None = None
    v4_prompt_compress_enabled: bool = True
    v4_prompt_compress_threshold_tokens: int = 2000
    v4_prompt_compress_target_ratio: float = 0.3
    v4_prompt_compress_default_mode: str = "bullet"
    v4_prompt_compress_coverage_mode: str = "heuristic"
    v4_character_validation_mode: str = "heuristic"
    v6_enabled: bool = True
    v6_simulation_store_max_rows_per_file: int = 500
    v6_simulation_store_max_bytes_per_file: int = 2_000_000
    v6_observability_latency_p95_ms_threshold: float = 1200.0
    v6_observability_error_rate_threshold: float = 0.1
    v6_observability_fallback_rate_threshold: float = 0.4
    v6_graph_memory_max_in_memory_rows: int = 5000
    v6_graph_memory_max_age_hours: int = 168
    v6_graph_memory_chapter_window: int = 20
    v6_graph_memory_min_token_overlap: float = 0.2
    v6_graph_memory_compaction_max_rows: int = 5000
    v6_graph_memory_audit_max_rows: int = 500
    v6_graph_memory_audit_expired_rate_threshold: float = 0.25
    v6_graph_memory_audit_duplicate_groups_threshold: int = 10
    v6_graph_memory_audit_active_drop_rate_threshold: float = 0.5
    v6_graph_memory_source_weights_json: str | None = None
    v7_enabled: bool = True
    v7_opening_gate_enabled: bool = True
    v7_antipattern_guard_enabled: bool = True
    v7_deadlock_router_enabled: bool = True
    v7_sampler_timeout_ms: int = 3000
    v7_llm_judge_max_tokens: int = 512
    v8_workbench_enabled: bool = True
    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
