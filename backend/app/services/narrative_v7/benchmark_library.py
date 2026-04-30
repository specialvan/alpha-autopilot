from __future__ import annotations

from .benchmark_store import V7BenchmarkStore
from .schemas import BenchmarkIngestRequest, BenchmarkIngestResponse, BenchmarkQueryRequest, BenchmarkQueryResponse


class BenchmarkLibrary:
    def __init__(self, *, store: V7BenchmarkStore) -> None:
        self._store = store

    def ingest_sample(self, payload: BenchmarkIngestRequest) -> BenchmarkIngestResponse:
        return self._store.ingest(payload)

    def query_benchmark(self, payload: BenchmarkQueryRequest) -> BenchmarkQueryResponse:
        return self._store.query(payload)

    def retract_sample(self, book_id: str) -> bool:
        return self._store.retract(book_id)
