# mrn/core/block_base.py
from __future__ import annotations
from typing import Dict, Callable, Any

class BlockWithSchema:
    """
    Base de bloco para o DSL e o runner:
      - schema: dict[porta][campo] -> reader(signal)->float
      - read_port(name): retorna um objeto com os atributos necessários p/ readers
      - merge_partial(attr, value): recebe parciais (ex.: mu/lam) antes do compute()
      - compute(): produz as saídas internas (ex.: complete/classified)
    """
    def __init__(self, block_id: str):
        self.block_id = block_id
        self._graph = None  # setado quando add no BlockGraph
        self._schema: Dict[str, Dict[str, Callable[[Any], float]]] = {}

    # --- usados pela DSL ---
    def has_attr(self, port: str, attr: str) -> bool:
        return port in self._schema and attr in self._schema[port]

    def reader(self, port: str, attr: str) -> Callable[[Any], float]:
        try:
            return self._schema[port][attr]
        except KeyError:
            raise AttributeError(f"Campo '{attr}' não existe na porta '{port}' do bloco '{self.block_id}'.")

    # --- usados pelo runner ---
    def read_port(self, name: str) -> Any:
        raise NotImplementedError

    def merge_partial(self, attr: str, value: float) -> None:
        raise NotImplementedError

    def compute(self) -> None:
        raise NotImplementedError
