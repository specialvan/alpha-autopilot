from __future__ import annotations

from time import perf_counter

from .common import clamp
from .schemas import (
    BenchmarkParameterSet,
    NQMSampleRequest,
    NQMSampleResponse,
    NQMVector,
    NarrativeMetricOHLCV,
    default_nqm_metrics,
)


_CONFLICT_KEYWORDS = ("冲突", "危机", "对抗", "背叛", "追杀", "死", "威胁", "倒计时")
_HOOK_KEYWORDS = ("?", "？", "为什么", "真相", "秘密", "到底")
_REWARD_KEYWORDS = ("奖励", "突破", "升级", "觉醒", "宝物", "逆袭")
_SOCIAL_KEYWORDS = ("众人", "围观", "全场", "震惊", "欢呼", "掌声")
_SENSORY_KEYWORDS = ("看见", "听见", "触到", "气味", "冷", "热", "疼", "光")


class NQMSampler:
    """PR-AA-28: deterministic first-pass NQM sampler."""

    def sample(self, payload: NQMSampleRequest) -> NQMSampleResponse:
        started_at = perf_counter()
        text = payload.text
        char_count = max(1, len(text))

        metrics = default_nqm_metrics()
        conflict_density = _keyword_density(text, _CONFLICT_KEYWORDS)
        hook_density = _keyword_density(text, _HOOK_KEYWORDS)
        reward_density = _keyword_density(text, _REWARD_KEYWORDS)
        social_density = _keyword_density(text, _SOCIAL_KEYWORDS)
        sensory_density = _keyword_density(text, _SENSORY_KEYWORDS)

        # P layer
        metrics["P1"] = clamp(0.55 + 0.20 * (1.0 - conflict_density * 0.5))
        metrics["P2"] = clamp(0.58 + 0.15 * (1.0 - abs(_quote_ratio(text) - 0.28)))
        metrics["P3"] = clamp(0.50 + 0.35 * conflict_density)
        metrics["P4"] = clamp(0.55 + 0.15 * min(1.0, len(payload.character_states) / 6.0))
        metrics["P5"] = clamp(0.45 + 0.45 * _countdown_signal(text))
        metrics["P6"] = clamp(0.45 + 0.40 * _dialogue_identity_proxy(text))
        metrics["P7"] = clamp(0.55 + 0.25 * (1.0 - _pov_jump_proxy(text)))

        # T layer
        metrics["T1"] = clamp(0.50 + 0.30 * _structure_signal(text))
        metrics["T2"] = clamp(0.45 + 0.45 * conflict_density)
        metrics["T3"] = clamp(0.48 + 0.35 * reward_density)
        metrics["T4"] = clamp(hook_density)
        metrics["T5"] = clamp(0.45 + 0.35 * (conflict_density + reward_density) / 2.0)
        metrics["T6"] = clamp(0.35 + 0.45 * _random_reward_signal(text))
        metrics["T7"] = clamp(0.35 + 0.50 * social_density)
        metrics["T8"] = clamp(0.40 + 0.35 * _opening_hook_signal(text))
        metrics["T9"] = clamp(0.42 + 0.40 * _antagonist_pressure_signal(text))
        metrics["T10"] = clamp(0.40 + 0.45 * sensory_density)

        # W layer
        metrics["W1"] = clamp(0.70 - 0.20 * _rule_violation_signal(text))
        metrics["W2"] = clamp(0.45 + 0.35 * _info_velocity_signal(text))
        metrics["W3"] = clamp(0.45 + 0.35 * hook_density)
        metrics["W4"] = clamp(0.48 + 0.30 * conflict_density)
        metrics["W5"] = clamp(0.42 + 0.45 * _conflict_layer_signal(text))
        metrics["W6"] = clamp(0.40 + 0.40 * _death_payoff_signal(text))

        # A layer
        benchmark = payload.benchmark_parameters or BenchmarkParameterSet()
        target = benchmark.nqm_mean
        metrics["A1"] = clamp(1.0 - abs(_rough_quality_proxy(text) - target))
        metrics["A2"] = clamp(0.55 + 0.20 * min(1.0, len(payload.character_states) / 5.0))
        metrics["A3"] = clamp(0.45 + 0.35 * _causality_signal(text))
        metrics["A4"] = clamp(0.50 + 0.30 * _retention_alignment_signal(text))
        metrics["A5"] = clamp(0.40 + 0.45 * _reversal_signal(text))
        metrics["A6"] = clamp(1.0 - abs(_rough_quality_proxy(text) - benchmark.nqm_mean) / max(0.01, benchmark.nqm_std * 2.0))

        composite = _composite(metrics)
        prev_close = float(payload.story_state.get("prev_nqm_close", composite - 0.03))
        open_value = clamp(prev_close)
        high_value = clamp(max(open_value, composite) + 0.05)
        low_value = clamp(min(open_value, composite) - 0.05)
        volume = max(0.0, 1000.0 * (metrics["T4"] + metrics["T5"] + metrics["T7"] + metrics["A4"]) / 4.0)
        if isinstance(payload.story_state.get("reader_signal_volume"), (int, float)):
            volume = max(volume, float(payload.story_state["reader_signal_volume"]))

        response = NQMSampleResponse(
            vector=NQMVector(metrics=metrics, composite=composite),
            ohlcv=NarrativeMetricOHLCV(
                open=open_value,
                high=high_value,
                low=low_value,
                close=composite,
                volume=volume,
            ),
            elapsed_ms=(perf_counter() - started_at) * 1000.0,
        )
        return response


def _keyword_density(text: str, keywords: tuple[str, ...]) -> float:
    lowered = text.lower()
    hits = 0
    for keyword in keywords:
        hits += lowered.count(keyword.lower())
    return clamp(hits / max(1.0, len(text) / 260.0))


def _quote_ratio(text: str) -> float:
    quoted = text.count("“") + text.count('"')
    return clamp(quoted / max(1.0, len(text) / 80.0))


def _countdown_signal(text: str) -> float:
    signal_keywords = ("今天", "今晚", "三天", "倒计时", "最后", "立刻", "马上")
    return _keyword_density(text, signal_keywords)


def _dialogue_identity_proxy(text: str) -> float:
    dialogue_lines = text.count("“") + text.count("”")
    punctuation = text.count("！") + text.count("?") + text.count("？")
    return clamp((dialogue_lines + punctuation) / max(1.0, len(text) / 50.0))


def _pov_jump_proxy(text: str) -> float:
    pronouns = text.count("我") + text.count("他") + text.count("她") + text.count("你")
    pov_markers = text.count("心想") + text.count("忽然觉得")
    return clamp((pronouns * 0.03 + pov_markers * 0.12) / 2.0)


def _structure_signal(text: str) -> float:
    return clamp((text.count("于是") + text.count("然后") + text.count("结果")) / max(1.0, len(text) / 240.0))


def _random_reward_signal(text: str) -> float:
    random_markers = ("突然", "意外", "竟然", "没想到", "随机")
    return _keyword_density(text, random_markers)


def _opening_hook_signal(text: str) -> float:
    head = text[: max(120, min(len(text), 420))]
    conflict = _keyword_density(head, _CONFLICT_KEYWORDS)
    hook = _keyword_density(head, _HOOK_KEYWORDS)
    protagonist = 1.0 if any(token in head for token in ("我", "主角", "他", "她")) else 0.0
    return clamp((conflict + hook + protagonist) / 3.0)


def _antagonist_pressure_signal(text: str) -> float:
    markers = ("敌人", "反派", "压制", "封锁", "围剿", "碾压")
    return _keyword_density(text, markers)


def _rule_violation_signal(text: str) -> float:
    markers = ("前后矛盾", "突然改口", "设定崩")
    return _keyword_density(text, markers)


def _info_velocity_signal(text: str) -> float:
    info_markers = ("原来", "真相", "揭露", "情报", "线索")
    density = _keyword_density(text, info_markers)
    return clamp(1.0 - abs(0.45 - density) * 1.6)


def _conflict_layer_signal(text: str) -> float:
    external = _keyword_density(text, ("战斗", "争夺", "对抗", "追捕"))
    internal = _keyword_density(text, ("犹豫", "纠结", "不敢", "不得不"))
    systemic = _keyword_density(text, ("规则", "阶层", "制度", "命运"))
    covered = sum(1 for value in (external, internal, systemic) if value >= 0.2)
    return clamp(covered / 3.0)


def _death_payoff_signal(text: str) -> float:
    if "死亡" not in text and "牺牲" not in text and "退场" not in text:
        return 0.55
    grief = _keyword_density(text, ("遗憾", "怀念", "痛", "祭奠", "余波"))
    return clamp(0.45 + 0.50 * grief)


def _rough_quality_proxy(text: str) -> float:
    length_component = clamp(len(text) / 2500.0)
    lexical_component = clamp(len(set(text)) / max(1.0, len(text)) * 8.0)
    return clamp((length_component + lexical_component) / 2.0)


def _causality_signal(text: str) -> float:
    markers = ("因为", "所以", "导致", "因此", "于是")
    return _keyword_density(text, markers)


def _retention_alignment_signal(text: str) -> float:
    markers = ("下一章", "继续", "未完", "悬念", "等待")
    return _keyword_density(text, markers)


def _reversal_signal(text: str) -> float:
    markers = ("反转", "真相", "其实", "原来", "翻盘", "骗局")
    return _keyword_density(text, markers)


def _composite(metrics: dict[str, float]) -> float:
    p_avg = sum(metrics[key] for key in metrics if key.startswith("P")) / 7.0
    t_avg = sum(metrics[key] for key in metrics if key.startswith("T")) / 10.0
    w_avg = sum(metrics[key] for key in metrics if key.startswith("W")) / 6.0
    a_avg = sum(metrics[key] for key in metrics if key.startswith("A")) / 6.0
    return clamp(p_avg * 0.20 + t_avg * 0.30 + w_avg * 0.15 + a_avg * 0.35)
