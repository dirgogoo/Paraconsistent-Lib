from typing import List
from mrn.core.isignal import ISignal

class INetworkNode:
    def get_id(self) -> str:
        ...

    def set_id(self, id :str):
        ...

    def receive(self, signal: ISignal) -> None:
        ...

    def propagate(self) -> List[ISignal]:
        ...

    def reset(self) -> None:
        ...

    def get_outputs(self) -> List[ISignal]:
        ...
