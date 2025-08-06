from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.ilogic_calculation import ICalculation
from mrn.core.isignal import ISignal

class ParaconsistentParserOperation(IOperation):
    def __init__(self, calculator: ICalculation):
        self.calculator = calculator

    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        return [self.calculator.process(signal) for signal in inputs]

    def name(self) -> str:
        return "ParaconsistentOperation"