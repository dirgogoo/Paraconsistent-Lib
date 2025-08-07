from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.icalculation import ICalculation
from mrn.core.isignal import ISignal

class NoneOperation(IOperation):
    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        return inputs

    def name(self) -> str:
        return "NoneOperation"