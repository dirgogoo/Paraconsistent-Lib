from mrn.core.icalculation import ICalculation
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.signals.classified_paraconsistent_signal import ClassifiedParaconsistentSignal

class ThresholdClassifierCalculation(ICalculation):
    def __init__(self, threshold: float = 0.3):
        self.threshold = threshold
        self._last_result = None

    def process(self, signal: CompleteParaconsistentSignal) -> "ThresholdClassifierCalculation":
        label = "V" if signal.gc > self.threshold else "F"
        confidence = abs(signal.gc)
        self._last_result = ClassifiedParaconsistentSignal(label, confidence, signal.source_id)
        return self

    def result(self) -> ClassifiedParaconsistentSignal:
        return self._last_result
