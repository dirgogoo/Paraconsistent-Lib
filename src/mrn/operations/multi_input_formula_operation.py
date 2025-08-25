# exemplo de operation p/ ponte multi-entrada
from typing import List, Callable
from mrn.core.ioperation import IOperation
from mrn.core.isignal import ISignal
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal

class MultiInputFormulaOperation(IOperation):
    def __init__(self, func: Callable[[List[ISignal]], float], to_attr: str):
        self.func = func
        self.to_attr = to_attr

    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        val = float(self.func(inputs))
        if self.to_attr == "mu":
            return [SimpleParaconsistentSignal(mu=val, lam=0.0)]
        else:
            return [SimpleParaconsistentSignal(mu=0.0, lam=val)]

    def name(self) -> str:
        return "MultiInputFormulaOperation"
