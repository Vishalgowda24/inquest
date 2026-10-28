from __future__ import annotations
from typing import Protocol
from inquest.contracts import Candidate, VerificationFinding

class VerifyMethod(Protocol):
    name: str
    def run(self, candidates: list[Candidate], context: dict[str, object], vault: dict[str, dict[str, object]]) -> list[VerificationFinding]: ...
