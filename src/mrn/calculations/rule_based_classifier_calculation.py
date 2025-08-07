from mrn.core.icalculation import ICalculation
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.signals.classified_paraconsistent_signal import ClassifiedParaconsistentSignal

class RuleBasedClassifierCalculation(ICalculation):
    def __init__(self, rules: dict):
        self.rules = rules  # Ex: {"V": lambda s: s.gc > 0.5, "F": lambda s: s.gc < -0.5}
        self._last_result = None

    def process(self, signal: CompleteParaconsistentSignal) -> "RuleBasedClassifierCalculation":
        for label, condition in self.rules.items():
            if condition(signal):
                self._last_result = ClassifiedParaconsistentSignal(label, signal.gc, signal.source_id)
                return self
        self._last_result = ClassifiedParaconsistentSignal("⊥", 0.0, signal.source_id)
        return self

    def result(self) -> ClassifiedParaconsistentSignal:
        return self._last_result
