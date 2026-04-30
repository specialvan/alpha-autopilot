from __future__ import annotations

from .benchmark_store import V7BenchmarkStore
from .schemas import (
    BenchmarkIngestRequest,
    BenchmarkIngestResponse,
    BenchmarkQueryRequest,
    BenchmarkQueryResponse,
    BenchmarkRestoreResponse,
    BenchmarkVersionRecord,
)


class BenchmarkLibrary:
    def __init__(self, *, store: V7BenchmarkStore) -> None:
        self._store = store

    def ingest_sample(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        return self._store.ingest(payload)

    def query_benchmark(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        return self._store.query(payload)

    def retract_sample(self, book_id: str) -> bool:
        return self._store.retract(book_id)

    def list_versions(self, *, limit: int = 20) -> list[BenchmarkVersionRecord]:
        return self._store.list_versions(limit=limit)

    def restore_version(self, version: str) -> BenchmarkRestoreResponse:
        return self._store.restore(version)
