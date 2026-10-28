"""Independent stage plugin registration."""

from __future__ import annotations

from typing import Protocol

from inquest.contracts import StageInput, StageResult
from .context import RunContext
from .errors import StageError


class StagePlugin(Protocol):
    name: str

    def run(self, ctx: RunContext, inp: StageInput) -> StageResult: ...


class StageRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, StagePlugin] = {}

    def register(self, plugin: StagePlugin) -> None:
        if plugin.name in self._plugins:
            raise StageError(f"Stage already registered: {plugin.name}", stage=plugin.name)
        self._plugins[plugin.name] = plugin

    def get(self, name: str) -> StagePlugin:
        try:
            return self._plugins[name]
        except KeyError as exc:
            raise StageError(f"Unknown stage: {name}", stage=name) from exc

    def names(self) -> tuple[str, ...]:
        return tuple(self._plugins)
