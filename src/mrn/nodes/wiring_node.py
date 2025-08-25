from __future__ import annotations
from typing import List, Optional, Callable
from mrn.core.inetwork_node import INetworkNode
from mrn.core.isignal import ISignal

class WiringNode(INetworkNode):
    """
    Nó simples para o DSL:
      - operation == None: repassa sinais (identidade)
      - operation(callable): recebe List[ISignal] e devolve List[ISignal]
    """
    def __init__(self, node_id: str, operation: Optional[Callable[[List[ISignal]], List[ISignal]]] = None):
        self._id = node_id
        self._op = operation
        self._inbox: List[ISignal] = []
        self._outbox: List[ISignal] = []

    def get_id(self) -> str: return self._id
    def set_id(self, id: str): self._id = id

    def receive(self, signal: ISignal) -> None:
        self._inbox.append(signal)

    def propagate(self) -> List[ISignal]:
        if self._op is None:
            self._outbox = list(self._inbox)
        else:
            self._outbox = list(self._op(self._inbox))
        self._inbox.clear()
        return list(self._outbox)

    def reset(self) -> None:
        self._inbox.clear()
        self._outbox.clear()

    def get_outputs(self) -> List[ISignal]:
        return list(self._outbox)
