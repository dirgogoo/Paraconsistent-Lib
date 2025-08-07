from typing import Dict, List
from collections import deque
from mrn.core.inetwork_node import INetworkNode
from mrn.core.isignal import ISignal

class Network_Manager:
    def __init__(self):
        self._nodes: Dict[str, INetworkNode] = {}
        self._edges: Dict[str, List[str]] = {}
        self._reverse_edges: Dict[str, List[str]] = {}
        self._id_counter: Dict[str, int] = {}

    def _generate_id(self, node: INetworkNode) -> str:
        cls_name = node.__class__.__name__
        count = self._id_counter.get(cls_name, 0) + 1
        self._id_counter[cls_name] = count
        return f"{cls_name}_{count}"

    def add_node(self, node: INetworkNode) -> None:
        node_id = node.get_id()
        
        if not node_id or node_id.strip() == "":
            node_id = self._generate_id(node)
            node.set_id(node_id)
        elif node_id in self._nodes:
            raise ValueError(f"ID duplicado detectado: '{node_id}'.")

        self._nodes[node_id] = node
        self._edges.setdefault(node_id, [])
        self._reverse_edges.setdefault(node_id, [])

    def connect(self, from_node: INetworkNode, to_node: INetworkNode) -> None:
        from_id = from_node.get_id()
        to_id = to_node.get_id()
        if from_id not in self._nodes or to_id not in self._nodes:
            raise ValueError("Tentando conectar nós que não existem na rede.")

        self._edges[from_id].append(to_id)
        self._reverse_edges[to_id].append(from_id)

    def reset_all(self) -> None:
        for node in self._nodes.values():
            node.reset()

    def _topological_order(self) -> List[str]:
        in_degree = {nid: len(self._reverse_edges[nid]) for nid in self._nodes}
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        order = []

        while queue:
            current = queue.popleft()
            order.append(current)
            for neighbor in self._edges.get(current, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self._nodes):
            raise ValueError("Ciclo detectado na rede. A topologia não é um DAG.")

        return order

    def propagate_all(self) -> None:
        order = self._topological_order()

        for node_id in order:
            node = self._nodes[node_id]
            #print(f"\n📡 Propagando {node_id}")
            outputs = node.propagate()

            for target_id in self._edges[node_id]:
                target = self._nodes[target_id]
                for signal in outputs:
                    # print(f"➡️ {node_id} -> {target_id} :: {signal.to_dict()}")
                    target.receive(signal.clone())

    def get_outputs(self, node: INetworkNode) -> List[ISignal]:
        node_id = node.get_id()
        return self._nodes[node_id].get_outputs() if node_id in self._nodes else []

    def get_all_outputs(self) -> Dict[str, List[ISignal]]:
        return {nid: n.get_outputs() for nid, n in self._nodes.items()}
