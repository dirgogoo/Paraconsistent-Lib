from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.isignal import ISignal

class IdentityOperation(IOperation):
    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        return inputs[:1]  # retorna apenas o primeiro sinal

    def name(self) -> str:
        return "Identity"