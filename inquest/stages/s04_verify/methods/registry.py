from inquest.core.errors import StageError
from .vault_evidence import VaultEvidenceMethod
from .dependency_path import DependencyPathMethod
from .temporal_consistency import TemporalConsistencyMethod
from .recovery_check import RecoveryCheckMethod
from .alternative_check import AlternativeCheckMethod

class VerifyMethodRegistry:
    def __init__(self): self._items={}
    def register(self,method):
        if method.name in self._items: raise StageError(f"Duplicate verification method: {method.name}",stage="s04_verify")
        self._items[method.name]=method
    def names(self): return tuple(self._items)
    def get(self,name):
        if name not in self._items: raise StageError(f"Unknown verification method: {name}",stage="s04_verify")
        return self._items[name]

def default_method_registry():
    r=VerifyMethodRegistry()
    for m in (VaultEvidenceMethod(),DependencyPathMethod(),TemporalConsistencyMethod(),RecoveryCheckMethod(),AlternativeCheckMethod()): r.register(m)
    return r
