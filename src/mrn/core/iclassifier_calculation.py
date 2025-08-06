from typing import List
from mrn.core.isignal import ISignal

class IClassifierCalculation:
    def classify(self, inputs: List[ISignal]) -> str:
        ...