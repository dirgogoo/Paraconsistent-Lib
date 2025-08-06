from typing import List
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.core.iclassifier_calculation import IClassifierCalculation

class ThresholdClassifierCalculation(IClassifierCalculation):
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold

    def classify(self, inputs: List[CompleteParaconsistentSignal]) -> str:
        if not inputs:
            return "⊥"

        avg_gc = sum(s.gc for s in inputs) / len(inputs)
        return "V" if avg_gc > self.threshold else "F"