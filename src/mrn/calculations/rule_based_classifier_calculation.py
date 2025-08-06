from typing import List
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.core.iclassifier_calculation import IClassifierCalculation

class RuleBasedClassifierCalculation(IClassifierCalculation):
    def __init__(self, rules: dict):
        self.rules = rules  # Ex: {"V": lambda x: x.gc > 0.5, "F": lambda x: x.gc < -0.5}

    def classify(self, inputs: List[CompleteParaconsistentSignal]) -> str:
        for label, condition in self.rules.items():
            if all(condition(s) for s in inputs):
                return label
        return "⊥"