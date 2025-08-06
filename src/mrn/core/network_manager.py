from typing import Dict, List, Set
from collections import deque
from mrn.core.inetwork_node import INetworkNode
from mrn.core.isignal import ISignal

class Network_Manager:
    def __init__(self):
        self._nodes: Dict[str, INetworkNode] = {}
        self._edges: Dict[str, List[str]] = {}           # forward connections
        self._reverse_edges: Dict[str, List[str]] = {}   # for DAG traversal

    def add_node(self, node: INetworkNode) -> None:
        node_id = node.get_id()
        self._nodes[node_id] = node
        self._edges[node_id] = []
        self._reverse_edges[node_id] = []

    def connect(self, from_id: str, to_id: str) -> None:
        if from_id in self._nodes and to_id in self._nodes:
            self._edges[from_id].append(to_id)
            self._reverse_edges[to_id].append(from_id)

    def reset_all(self) -> None:
        for node in self._nodes.values():
            node.reset()

    def _topological_order(self) -> List[str]:
        # Kahn's algorithm
        in_degree = {node_id: len(self._reverse_edges[node_id]) for node_id in self._nodes}
        queue = deque([node_id for node_id, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self._edges.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._nodes):
            raise ValueError("Ciclo detectado na rede lógica. Não é um DAG válido.")

        return order

    def propagate_all(self) -> None:
        order = self._topological_order()

        for node_id in order:
            node = self._nodes[node_id]
            outputs = node.propagate()
            for target_id in self._edges[node_id]:
                target = self._nodes[target_id]
                for signal in outputs:
                    target.receive(signal.clone())

    def get_outputs(self, node_id: str) -> List[ISignal]:
        return self._nodes[node_id].get_outputs() if node_id in self._nodes else []

    def get_all_outputs(self) -> Dict[str, List[ISignal]]:
        return {nid: n.get_outputs() for nid, n in self._nodes.items()}