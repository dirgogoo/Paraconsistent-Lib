from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.icalculation import ICalculation
from mrn.core.isignal import ISignal

class ResultEachSignalOperation(IOperation):
    def __init__(self, calculator: ICalculation):
        self.calculator = calculator

    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        return [self.calculator.process(signal).result() for signal in inputs]

    def name(self) -> str:
        return "ResultEachSignalOperation"