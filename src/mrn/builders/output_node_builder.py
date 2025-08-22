from mrn.nodes.output_node import OutputNode
from mrn.core.ioperation import IOperation
from .base_node_builder import BaseNodeBuilder

class OutputNodeBuilder(BaseNodeBuilder):
    def __init__(self):
        super().__init__()
        self._operation: IOperation = None

    def set_operation(self, operation: IOperation) -> "OutputNodeBuilder":
        self._operation = operation
        return self

    def build(self) ->  OutputNode:
        if not self._operation:
            raise ValueError(" OutputNode requires an operation.")
        return  OutputNode(node_id=self.get_id(), operation=self._operation)