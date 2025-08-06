from typing import List
from mrn.core.isignal import ISignal
from mrn.core.inetwork_node import INetworkNode

class InputNode(INetworkNode):
    def __init__(self, node_id: str):
        self.node_id = node_id
        self._signals: List[ISignal] = []

    def get_id(self) -> str:
        return self.node_id

    def receive(self, signal: ISignal) -> None:
        self._signals.append(signal)

    def propagate(self) -> List[ISignal]:
        return self._signals.copy()

    def get_outputs(self) -> List[ISignal]:
        return self._signals.copy()

    def reset(self) -> None:
        self._signals.clear()