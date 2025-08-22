from dataclasses import dataclass
from typing import Dict, Any
from ..core.isignal import ISignal

@dataclass
class CompleteParaconsistentSignal(ISignal):
    mu: float
    lam: float
    gc: float
    gct: float
    gcr: float
    mer: float
    phie: float
    source_id: str = ""

    def get_certainty(self) -> float:
        return self.gc

    def is_empty(self) -> bool:
        return self.mu == 0.0 and self.lam == 0.0

    def clone(self) -> "CompleteParaconsistentSignal":
        return CompleteParaconsistentSignal(
            self.mu, self.lam, self.gc, self.gct, self.gcr, self.mer, self.phie, self.source_id
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paraconsistent_complete",
            "mu": self.mu,
            "lambda": self.lam,
            "gc": self.gc,
            "gct": self.gct,
            "gcr": self.gcr,
            "mer": self.mer,
            "phie": self.phie,
            "certainty": self.get_certainty(),
            "source": self.source_id
        }