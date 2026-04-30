from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json

from backend.app.services.narrative_v6.graph_memory_store import PersistentGraphMemoryStore
from backend.app.services.narrative_v6.schemas import GraphMemoryRecord, GraphRAGHit


def _record(
    *,
    record_id: str,
    query: str,
    source_route: str,
    summary: str,
    chapter_index: int,
    created_at_utc: str,
    hidden: bool = False,
) -> GraphMemoryRecord:
    return GraphMemoryRecord(
        record_id=record_id,
        query=query,
        query_tokens=[token.lower() for token in query.split()],
        source_route=source_route,
        chapter_index=chapter_index,
        simulation_id=None,
        node_id=f"{record_id}-node",
        node_type="relationship",
        summary=summary,
        evidence="evidence",
        score=0.8,
        confidence=0.8,
        hidden=hidden,
        created_at_utc=created_at_utc,
    )


def test_graph_memory_store_persists_and_recalls_hits(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    store = PersistentGraphMemoryStore(path=path, max_in_memory_rows=1000)

    store.append_hits(
        query="suchen betrayal northcity",
        hits=[
            GraphRAGHit(
                node_id="rel-1",
                node_type="relationship",
                summary="Suchen betrayed Linmo at North City gate.",
                score=0.82,
                confidence=0.86,
                evidence="chapter 6 conflict",
                hidden=False,
            )
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=6,
        simulation_id="sim-1",
    )

    reloaded = PersistentGraphMemoryStore(path=path, max_in_memory_rows=1000)
    recalled = reloaded.search_hits(
        query="betrayal northcity",
        top_k=3,
        include_hidden=False,
        chapter_index=6,
    )

    assert recalled
    assert recalled[0].node_type == "history_memory"
    assert "betrayed" in recalled[0].summary.lower()


def test_graph_memory_store_honors_hidden_filter(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    store = PersistentGraphMemoryStore(path=path, max_in_memory_rows=1000)

    store.append_hits(
        query="secret betrayal",
        hits=[
            GraphRAGHit(
                node_id="gm-1",
                node_type="group_memory",
                summary="North guard once suffered a hidden betrayal.",
                score=0.7,
                confidence=0.8,
                evidence="old archive",
                hidden=True,
            )
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=9,
    )

    without_hidden = store.search_hits(query="betrayal", include_hidden=False, top_k=3)
    with_hidden = store.search_hits(query="betrayal", include_hidden=True, top_k=3)

    assert not without_hidden
    assert with_hidden


def test_graph_memory_store_applies_chapter_window_filter(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        chapter_window=5,
    )
    store.append_hits(
        query="city wall battle",
        hits=[
            GraphRAGHit(
                node_id="rel-window",
                node_type="relationship",
                summary="Wall battle broke trust between commanders.",
                score=0.8,
                confidence=0.8,
                evidence="chapter 10",
            )
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=10,
    )

    recalled = store.search_hits(
        query="battle trust",
        top_k=3,
        chapter_index=25,
    )
    assert recalled == []


def test_graph_memory_store_applies_max_age_filter(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    now = datetime.now(timezone.utc)
    expired = (now - timedelta(hours=8)).isoformat().replace("+00:00", "Z")
    fresh = (now - timedelta(minutes=20)).isoformat().replace("+00:00", "Z")

    rows = [
        _record(
            record_id="old-1",
            query="betrayal city",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Old betrayal memory.",
            chapter_index=8,
            created_at_utc=expired,
        ),
        _record(
            record_id="new-1",
            query="betrayal city",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Fresh betrayal memory.",
            chapter_index=8,
            created_at_utc=fresh,
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        max_age_hours=2,
    )
    recalled = store.search_hits(
        query="betrayal city",
        top_k=3,
        chapter_index=8,
    )

    assert len(recalled) == 1
    assert "fresh" in recalled[0].summary.lower()


def test_graph_memory_store_uses_source_weight_for_ranking(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    rows = [
        _record(
            record_id="route-low",
            query="alliance fracture",
            source_route="/api/narrative/v6/characters/{character_id}/interview",
            summary="Alliance fracture noted in interview.",
            chapter_index=12,
            created_at_utc=now,
        ),
        _record(
            record_id="route-high",
            query="alliance fracture",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Alliance fracture confirmed by graph retrieval.",
            chapter_index=12,
            created_at_utc=now,
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        source_weights={
            "/api/narrative/v6/characters/{character_id}/interview": 0.9,
            "/api/narrative/v6/graph/retrieve": 1.3,
        },
    )
    recalled = store.search_hits(
        query="alliance fracture",
        top_k=2,
        chapter_index=12,
    )

    assert len(recalled) == 2
    assert "graph retrieval" in recalled[0].summary.lower()


def test_graph_memory_store_filters_semantic_drift_by_overlap_threshold(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        min_token_overlap=0.5,
    )
    store.append_hits(
        query="betrayal city gate",
        hits=[
            GraphRAGHit(
                node_id="drift-1",
                node_type="relationship",
                summary="Betrayal near the city gate.",
                score=0.8,
                confidence=0.8,
                evidence="chapter 6",
            )
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=6,
    )

    recalled = store.search_hits(
        query="betrayal unrelated distant",
        top_k=3,
        chapter_index=6,
    )

    assert recalled == []


def test_graph_memory_store_compacts_expired_and_duplicate_rows(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    now = datetime.now(timezone.utc)
    expired = (now - timedelta(hours=8)).isoformat().replace("+00:00", "Z")
    fresh_old = (now - timedelta(minutes=30)).isoformat().replace("+00:00", "Z")
    fresh_new = now.isoformat().replace("+00:00", "Z")
    rows = [
        _record(
            record_id="expired-1",
            query="betrayal city",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Expired betrayal memory.",
            chapter_index=8,
            created_at_utc=expired,
        ),
        _record(
            record_id="dup-old",
            query="alliance fracture",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Alliance fracture memory.",
            chapter_index=12,
            created_at_utc=fresh_old,
        ),
        _record(
            record_id="dup-new",
            query="alliance fracture",
            source_route="/api/narrative/v6/graph/retrieve",
            summary="Alliance fracture memory.",
            chapter_index=12,
            created_at_utc=fresh_new,
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row.model_dump(mode="json"), ensure_ascii=False))
            handle.write("\n")

    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        max_age_hours=2,
        compaction_max_rows=1000,
    )
    stats = store.compact()
    reloaded = PersistentGraphMemoryStore(path=path, max_in_memory_rows=1000)
    recalled = reloaded.search_hits(
        query="alliance fracture",
        top_k=3,
        chapter_index=12,
    )

    assert stats == {"before": 3, "after": 1, "removed": 2}
    assert len(recalled) == 1
    assert "Alliance fracture memory." == recalled[0].summary


def test_graph_memory_store_builds_audit_snapshot(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    store = PersistentGraphMemoryStore(
        path=path,
        max_in_memory_rows=1000,
        min_token_overlap=0.35,
        chapter_window=7,
    )
    store.append_hits(
        query="betrayal city",
        hits=[
            GraphRAGHit(
                node_id="audit-1",
                node_type="relationship",
                summary="Audit visible betrayal memory.",
                score=0.8,
                confidence=0.8,
                evidence="chapter 6",
            ),
            GraphRAGHit(
                node_id="audit-2",
                node_type="group_memory",
                summary="Audit hidden group memory.",
                score=0.7,
                confidence=0.7,
                evidence="chapter 6",
                hidden=True,
            ),
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=6,
    )

    snapshot = store.audit_snapshot(limit=1)

    assert snapshot["total_rows"] == 2
    assert snapshot["active_rows"] == 2
    assert snapshot["hidden_rows"] == 1
    assert snapshot["chapter_min"] == 6
    assert snapshot["chapter_max"] == 6
    assert snapshot["by_source_route"] == {"/api/narrative/v6/graph/retrieve": 2}
    assert snapshot["by_node_type"] == {"group_memory": 1, "relationship": 1}
    assert snapshot["policy"]["min_token_overlap"] == 0.35
    assert snapshot["policy"]["chapter_window"] == 7
    assert len(snapshot["latest_records"]) == 1


def test_graph_memory_store_persists_and_reads_audit_history(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    audit_path = tmp_path / "v6_graph_memory_audit.jsonl"
    store = PersistentGraphMemoryStore(
        path=path,
        audit_path=audit_path,
        max_in_memory_rows=1000,
        audit_max_rows=2,
    )
    store.append_hits(
        query="betrayal city",
        hits=[
            GraphRAGHit(
                node_id="audit-history-1",
                node_type="relationship",
                summary="Audit history betrayal memory.",
                score=0.8,
                confidence=0.8,
                evidence="chapter 6",
            )
        ],
        source_route="/api/narrative/v6/graph/retrieve",
        chapter_index=6,
    )

    first = store.persist_audit_snapshot(limit=1)
    second = store.persist_audit_snapshot(limit=1)
    third = store.persist_audit_snapshot(limit=1)
    history = store.audit_history(limit=5)

    assert audit_path.exists()
    assert first["total_rows"] == 1
    assert second["total_rows"] == 1
    assert third["total_rows"] == 1
    assert len(history) == 2
    assert all(item["total_rows"] == 1 for item in history)
    assert all(item["audit_path"] == str(audit_path) for item in history)


def test_graph_memory_store_builds_audit_trend_alerts(tmp_path) -> None:
    path = tmp_path / "v6_graph_memory.jsonl"
    audit_path = tmp_path / "v6_graph_memory_audit.jsonl"
    store = PersistentGraphMemoryStore(
        path=path,
        audit_path=audit_path,
        max_in_memory_rows=1000,
        audit_expired_rate_threshold=0.25,
        audit_duplicate_groups_threshold=1,
        audit_active_drop_rate_threshold=0.4,
    )
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "created_at_utc": "2026-05-01T00:00:00Z",
            "total_rows": 10,
            "active_rows": 10,
            "expired_rows": 0,
            "duplicate_groups": 0,
        },
        {
            "created_at_utc": "2026-05-01T01:00:00Z",
            "total_rows": 10,
            "active_rows": 3,
            "expired_rows": 4,
            "duplicate_groups": 2,
        },
    ]
    with audit_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")

    alerts = store.audit_trend_alerts(limit=5)
    codes = {item["code"] for item in alerts["alerts"]}

    assert alerts["history_count"] == 2
    assert alerts["expired_rate"] == 0.4
    assert alerts["active_drop_rate"] == 0.7
    assert alerts["duplicate_groups"] == 2
    assert codes == {
        "graph_memory_expired_rate_high",
        "graph_memory_duplicate_groups_high",
        "graph_memory_active_rows_drop",
    }
