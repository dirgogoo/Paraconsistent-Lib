# mrn/wiring/block_with_schema.py
from __future__ import annotations
from typing import Callable, Dict, List
from mrn.core.network_manager import Network_Manager
from mrn.core.isignal import ISignal
from mrn.core.inetwork_node import INetworkNode

class BlockWithSchema:
    """
    Base de bloco para o DSL:
      - mantém schema de leitura {_io_schema}
      - registra nós (INetworkNode) na Network_Manager
      - delega a port(name) e build_bridge_operation(...)
    """
    def __init__(self, *, block_id: str, network: Network_Manager | None = None):
        self.block_id = block_id
        self.net: Network_Manager = network or Network_Manager()
        self._all_nodes: List[INetworkNode] = []
        self._io_schema: Dict[str, Dict[str, Callable[[ISignal], float]]] = {}

    def _register_nodes(self, *nodes: INetworkNode) -> None:
        self._all_nodes.extend(nodes)
        self.net.add_node(*nodes)

    def has_attr(self, port: str, attr: str) -> bool:
        return port in self._io_schema and attr in self._io_schema[port]

    def get_reader(self, port: str, attr: str):
        try:
            return self._io_schema[port][attr]
        except KeyError:
            raise AttributeError(f"Campo '{attr}' não existe em '{port}'.")

    # Implementar nas subclasses
    def port(self, name: str) -> INetworkNode:
        raise NotImplementedError

    def build_bridge_operation(self, *, to_attr: str, func: Callable[[List[ISignal]], float]):
        """
        Deve retornar um IOperation que:
          - recebe TODOS os ISignal de entrada (em uma lista, na ordem das origens da expressão);
          - calcula um float via 'func(inputs)';
          - constrói um sinal de ENTRADA do bloco destino, escrevendo em 'to_attr' (ex.: 'mu' ou 'lam').
        """
        raise NotImplementedError

    # Conectores “bonitos” – import tardio para evitar ciclo
    @property
    def input(self):
        from mrn.wiring.dsl_refs import PortRef
        return PortRef(self, "in")

    @property
    def complete(self):
        from mrn.wiring.dsl_refs import PortRef
        return PortRef(self, "complete")

    @property
    def classified(self):
        from mrn.wiring.dsl_refs import PortRef
        return PortRef(self, "classified")
