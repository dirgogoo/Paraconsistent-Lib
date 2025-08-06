from dataclasses import dataclass
from typing import Dict, Any
from ..core.isignal import ISignal

@dataclass
class SimpleParaconsistentSignal(ISignal):
    mu: float
    lam: float
    source_id: str = ""

    def get_certainty(self) -> float:
        return self.mu - self.lam

    def is_empty(self) -> bool:
        return self.mu == 0.0 and self.lam == 0.0

    def clone(self) -> "SimpleParaconsistentSignal":
        return SimpleParaconsistentSignal(self.mu, self.lam, self.source_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paraconsistent",
            "mu": self.mu,
            "lambda": self.lam,
            "source": self.source_id,
            "certainty": self.get_certainty()
        }