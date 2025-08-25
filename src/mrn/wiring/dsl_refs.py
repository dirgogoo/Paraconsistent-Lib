from __future__ import annotations
from typing import Callable, TYPE_CHECKING
from mrn.core.isignal import ISignal
from mrn.nodes.wiring_node import WiringNode

if TYPE_CHECKING:
    from mrn.wiring.block_with_schema import BlockWithSchema  # só p/ type hints

class Expr:
    def __init__(self, reader: Callable[[ISignal], float]):
        self._f = reader
        self._src_block = None  # (block, port)

    def _bin(self, other, op):
        if isinstance(other, Expr):
            g = lambda s: op(self._f(s), other._f(s))
        else:
            c = float(other)
            g = lambda s: op(self._f(s), c)
        e = Expr(g); e._src_block = self._src_block; return e

    def __add__(self, o): return self._bin(o, lambda a,b:a+b)
    def __radd__(self, o): return self._bin(o, lambda a,b:b+a)
    def __sub__(self, o): return self._bin(o, lambda a,b:a-b)
    def __rsub__(self, o): return self._bin(o, lambda a,b:b-a)
    def __mul__(self, o): return self._bin(o, lambda a,b:a*b)
    def __truediv__(self, o): return self._bin(o, lambda a,b:a/b)
    def __pow__(self, o): return self._bin(o, lambda a,b:a**b)
    def __neg__(self): e = Expr(lambda s: -self._f(s)); e._src_block = self._src_block; return e
    def __abs__(self): e = Expr(lambda s: abs(self._f(s))); e._src_block = self._src_block; return e

    def __rshift__(self, dest_field: "FieldRef"):
        if self._src_block is None:
            raise RuntimeError("Expr sem origem associada (block,port).")
        src_block, src_port = self._src_block
        dest_block, dest_port, dest_attr = dest_field._owner, dest_field._port, dest_field._attr

        # garantir mesma rede
        if src_block.net is not dest_block.net:
            for n in dest_block._all_nodes:
                src_block.net.add_node(n)
            dest_block.net = src_block.net

        # criar nó-ponte (transforma float -> sinal de entrada do destino)
        op_node = WiringNode(
            node_id=f"bridge_{src_block.block_id}_{src_port}__to__{dest_block.block_id}_{dest_port}_{dest_attr}",
            operation=src_block.build_bridge_operation(to_attr=dest_attr, func=self._f),
        )
        g = src_block.net
        
        g.add_node(op_node)
        g.connect(src_block.port(src_port), op_node)
        g.connect(op_node, dest_block.port("in"))
        return dest_field

class FieldRef:
    def __init__(self, owner_block: "BlockWithSchema", port: str, attr: str):
        self._owner = owner_block
        self._port = port
        self._attr = attr

    def __rshift__(self, other: "FieldRef"):
        reader = self._owner.get_reader(self._port, self._attr)
        e = Expr(reader); e._src_block = (self._owner, self._port); return e >> other

    def _as_expr(self) -> Expr:
        reader = self._owner.get_reader(self._port, self._attr)
        e = Expr(reader); e._src_block = (self._owner, self._port); return e

    def __add__(self, o): return self._as_expr().__add__(o)
    def __radd__(self, o): return self._as_expr().__radd__(o)
    def __sub__(self, o): return self._as_expr().__sub__(o)
    def __rsub__(self, o): return self._as_expr().__rsub__(o)
    def __mul__(self, o): return self._as_expr().__mul__(o)
    def __truediv__(self, o): return self._as_expr().__truediv__(o)
    def __pow__(self, o): return self._as_expr().__pow__(o)
    def __neg__(self): return -self._as_expr()
    def __abs__(self): return abs(self._as_expr())

class PortRef:
    def __init__(self, owner_block: "BlockWithSchema", port: str):
        self._owner = owner_block
        self._port = port

    def __getattr__(self, attr: str) -> FieldRef:
        if not self._owner.has_attr(self._port, attr):
            raise AttributeError(f"Porta '{self._port}' não tem campo '{attr}' neste bloco.")
        return FieldRef(self._owner, self._port, attr)