class BaseNodeBuilder:
    def __init__(self):
        self._node_id = "default"

    def set_id(self, node_id: str) -> "BaseNodeBuilder":
        self._node_id = node_id
        return self

    def get_id(self) -> str:
        return self._node_id