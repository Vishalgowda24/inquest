"""Registry for independent candidate-method plugins."""

from __future__ import annotations

from typing import Protocol

from inquest.contracts import CandidateMethodResult, CanonicalBundle, SignalAnalysis


class CandidateMethod(Protocol):
    name: str

    def run(self, bundle: CanonicalBundle, signals: SignalAnalysis, vault_ids: set[str]) -> CandidateMethodResult: ...


class CandidateMethodRegistry:
    def __init__(self) -> None:
        self._methods: dict[str, CandidateMethod] = {}

    def register(self, method: CandidateMethod) -> None:
        if method.name in self._methods:
            raise ValueError(f"Candidate method already registered: {method.name}")
        self._methods[method.name] = method

    def get(self, name: str) -> CandidateMethod:
        return self._methods[name]

    def names(self) -> tuple[str, ...]:
        return tuple(self._methods)


def default_method_registry() -> CandidateMethodRegistry:
    from .change_based import ChangeBasedMethod
    from .graph_rwr import GraphRwrMethod
    from .temporal_lag import TemporalLagMethod
    from .trace_ochiai import TraceOchiaiMethod

    registry = CandidateMethodRegistry()
    for method in (ChangeBasedMethod(), GraphRwrMethod(), TraceOchiaiMethod(), TemporalLagMethod()):
        registry.register(method)
    return registry
