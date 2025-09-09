# mrn/core/graph.py
from __future__ import annotations
from typing import List, Callable, Tuple

class BlockWithSchema: ...  # só p/ type hints; import real no runtime circular.

Source = Tuple["BlockWithSchema", str, Callable[[object], float]]  # (block, port, reader)

class Connection:
    def __init__(self, sources: List[Source], func: Callable[[List[object]], float],
                 dest: "BlockWithSchema", dest_attr: str):
        self.sources = sources
        self.func = func
        self.dest = dest
        self.dest_attr = dest_attr

class BlockGraph:
    def __init__(self):
        self.blocks: list[BlockWithSchema] = []
        self.connections: list[Connection] = []

    def add_block(self, *blocks: "BlockWithSchema"):
        for b in blocks:
            b._graph = self
            self.blocks.append(b)

    def add_connection(self, conn: Connection):
        # guard simples contra ciclo direto (mesmo bloco em origem e destino)
        for (blk, _p, _r) in conn.sources:
            if blk is conn.dest:
                raise ValueError(
                    "Conexão criaria ciclo (bloco origem == bloco destino). "
                    "Use um bloco Delay/Memória para feedback."
                )
        self.connections.append(conn)

    def _topo_blocks(self) -> list["BlockWithSchema"]:
        deps = {b: set() for b in self.blocks}
        for c in self.connections:
            for (src, _p, _r) in c.sources:
                deps[c.dest].add(src)
        from collections import deque
        indeg = {b: len(deps[b]) for b in self.blocks}
        q = deque([b for b in self.blocks if indeg[b] == 0])
        order = []
        while q:
            u = q.popleft(); order.append(u)
            for v in self.blocks:
                if u in deps.get(v, ()):
                    indeg[v] -= 1
                    if indeg[v] == 0:
                        q.append(v)
        if len(order) != len(self.blocks):
            raise ValueError("Ciclo detectado no grafo de blocos. Insira Delay ou remodele conexões.")
        return order
    
    def incoming_of(self, block):
        return [c for c in self.connections if c.dest is block]

    def run(self):
        order = self._topo_blocks()
        # agrupar conexões por bloco destino
        by_dest = {b: [] for b in order}
        for c in self.connections:
            by_dest[c.dest].append(c)

        for b in order:
            # aplica todas as conexões que chegam no bloco b (gera parciais)
            for c in by_dest[b]:
                inputs = [src.read_port(port) for (src, port, _r) in c.sources]
                val = float(c.func(inputs))  # Expr multi-origem
                b.merge_partial(c.dest_attr, val)
            # depois computa o bloco (parser/classificador/etc.)
            b.compute()
