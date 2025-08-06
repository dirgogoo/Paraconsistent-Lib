from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.isignal import ISignal

from mrn.core.iclassifier_calculation import IClassifierCalculation
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.signals.classified_paraconsistent_signal import  ClassifiedParaconsistentSignal

class ClassifierOperation(IOperation):
    def __init__(self, classifier: IClassifierCalculation):
        self.classifier = classifier

    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        # Filtra apenas sinais do tipo completo
        pcs = [s for s in inputs if isinstance(s, CompleteParaconsistentSignal)]
        label = self.classifier.classify(pcs)
        confidence = sum(s.gc for s in pcs) / len(pcs) if pcs else 0.0

        return [ClassifiedParaconsistentSignal(label=label, confidence=confidence)]

    def name(self) -> str:
        return "ParaconsistentClassifier"