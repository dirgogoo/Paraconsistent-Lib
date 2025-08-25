from typing import List
from mrn.core.ioperation import IOperation
from mrn.core.isignal import ISignal


class GetLastSignalOperation(IOperation):
    """
    Mantém somente o último sinal do lote recebido no ciclo de propagação.
    - Se o sinal tiver .clone(), usa clone (compatível com Network_Manager que clona ao conectar).
    - Se não tiver, retorna o próprio objeto (duck-typing).
    """
    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        if not inputs:
            return []
        last = inputs[-1]
        try:
            return [last.clone()]
        except AttributeError:
            return [last]

    def name(self) -> str:
        return "GetLast"