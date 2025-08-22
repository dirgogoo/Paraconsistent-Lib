from mrn.nodes.logic_node import LogicNode
from mrn.core.ioperation import IOperation
from .base_node_builder import BaseNodeBuilder

class LogicNodeBuilder(BaseNodeBuilder):
    def __init__(self):
        super().__init__()
        self._operation: IOperation = None

    def set_operation(self, operation: IOperation) -> "LogicNodeBuilder":
        self._operation = operation
        return self

    def build(self) -> LogicNode:
        if not self._operation:
            raise ValueError("LogicNode requires an operation.")
        return LogicNode(node_id=self.get_id(), operation=self._operation)