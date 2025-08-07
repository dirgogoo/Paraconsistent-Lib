from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.icalculation import ICalculation
from mrn.core.isignal import ISignal

class UniqueResultAllSignalOperation(IOperation):
    def __init__(self, calculator: ICalculation):
        self.calculator = calculator

    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        for signal in inputs:
            self.calculator.process(signal)
        result = self.calculator.result()
        return [result] if result else []

    def name(self) -> str:
        return "UniqueResultAllSignalOperation"