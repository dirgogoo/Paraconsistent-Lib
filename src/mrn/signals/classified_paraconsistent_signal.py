from dataclasses import dataclass
from typing import Dict, Any
from ..core.isignal import ISignal

@dataclass
class ClassifiedParaconsistentSignal(ISignal):
    label: str
    confidence: float
    source_id: str = ""

    def get_certainty(self) -> float:
        return self.confidence

    def is_empty(self) -> bool:
        return self.label == "" or self.confidence == 0.0

    def clone(self) -> "ClassifiedParaconsistentSignal":
        return ClassifiedParaconsistentSignal(self.label, self.confidence, self.source_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "paraconsistent_output",
            "label": self.label,
            "confidence": self.confidence,
            "source": self.source_id
        }