# mrn/builders/input_node_builder.py
from mrn.nodes.input_node import InputNode
from .base_node_builder import BaseNodeBuilder

class InputNodeBuilder(BaseNodeBuilder):
    def build(self) -> InputNode:
        return InputNode(node_id=self.get_id())