from typing import List
from mrn.core.isignal import ISignal
from mrn.core.inetwork_node import INetworkNode
from mrn.core.ioperation import IOperation

class OutputNode(INetworkNode):
    def __init__(self, node_id: str, operation: IOperation):
        self.node_id = node_id
        self.operation = operation
        self._inputs: List[ISignal] = []
        self._outputs: List[ISignal] = []

    def get_id(self) -> str:
        return self.node_id

    def receive(self, signal: ISignal) -> None:
        self._inputs.append(signal)

    def propagate(self) -> List[ISignal]:
        self._outputs = self.operation.execute(self._inputs)
        return self._outputs

    def get_outputs(self) -> List[ISignal]:
        return self._outputs

    def reset(self) -> None:
        self._inputs.clear()
        self._outputs.clear()