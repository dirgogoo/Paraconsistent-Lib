# mrn/wiring/dsl_refs.py
from __future__ import annotations
from typing import Callable, List, Tuple, TYPE_CHECKING
from mrn.core.isignal import ISignal
from mrn.nodes.wiring_node import WiringNode

if TYPE_CHECKING:
    from mrn.wiring.block_with_schema import BlockWithSchema  # type hints

Origin = Tuple["BlockWithSchema", str, Callable[[ISignal], float]]  # (block, port, reader)

class Expr:
    """
    Expressão aritmética que pode combinar múltiplas origens (block/port).
    Armazena:
      - _sources: lista de origens [(block, port, reader), ...] na ordem esperada
      - _f_multi: Callable[[List[ISignal]], float]  -> usa 'inputs' na mesma ordem de _sources
    """
    def __init__(self, sources: List[Origin], f_multi: Callable[[List[ISignal]], float]):
        self._sources = sources
        self._f_multi = f_multi

    # ----- helpers p/ combinar duas Exprs preservando ordem -----
    @staticmethod
    def _combine(a: "Expr", b: "Expr", op: Callable[[float, float], float]) -> "Expr":
        len_a = len(a._sources)
        len_b = len(b._sources)
        sources = a._sources + b._sources

        def f_multi(inputs: List[ISignal]) -> float:
            va = a._f_multi(inputs[:len_a])
            vb = b._f_multi(inputs[len_a:len_a+len_b])
            return op(va, vb)

        return Expr(sources, f_multi)

    def _combine_const(self, c: float, op, swap: bool = False) -> "Expr":
        # expressão constante não precisa de origem; usa uma f_multi que ignora inputs
        const_expr = Expr([], lambda _: float(c))
        return Expr._combine(const_expr, self, op) if swap else Expr._combine(self, const_expr, op)

    # ----- aritmética -----
    def __add__(self, other):
        return self._combine(other, (lambda a,b: a+b) if isinstance(other, Expr) else None) \
            if isinstance(other, Expr) else self._combine_const(float(other), lambda a,b: a+b)
    def __radd__(self, other):
        return self._combine_const(float(other), lambda a,b: a+b, swap=True)

    def __sub__(self, other):
        return self._combine(other, (lambda a,b: a-b) if isinstance(other, Expr) else None) \
            if isinstance(other, Expr) else self._combine_const(float(other), lambda a,b: a-b)
    def __rsub__(self, other):
        return self._combine_const(float(other), lambda a,b: a-b, swap=True)

    def __mul__(self, other):
        return self._combine(other, (lambda a,b: a*b) if isinstance(other, Expr) else None) \
            if isinstance(other, Expr) else self._combine_const(float(other), lambda a,b: a*b)
    def __rmul__(self, other):
        return self._combine_const(float(other), lambda a,b: a*b, swap=True)

    def __truediv__(self, other):
        return self._combine(other, (lambda a,b: a/b) if isinstance(other, Expr) else None) \
            if isinstance(other, Expr) else self._combine_const(float(other), lambda a,b: a/b)
    def __rtruediv__(self, other):
        return self._combine_const(float(other), lambda a,b: a/b, swap=True)

    def __pow__(self, other):
        return self._combine(other, (lambda a,b: a**b) if isinstance(other, Expr) else None) \
            if isinstance(other, Expr) else self._combine_const(float(other), lambda a,b: a**b)

    def __neg__(self):
        return Expr(self._sources, lambda inputs: -self._f_multi(inputs))

    def __abs__(self):
        return Expr(self._sources, lambda inputs: abs(self._f_multi(inputs)))

    # ----- Expr >> FieldRef : cria o bridge multi-entrada -----
    def __rshift__(self, dest_field: "FieldRef"):
        dest_block, dest_port, dest_attr = dest_field._owner, dest_field._port, dest_field._attr

        # colocar todas as origens na MESMA rede do 1º bloco da lista
        if not self._sources:
            raise RuntimeError("Expressão sem origens. Use ao menos um FieldRef.")
        src_block0 = self._sources[0][0]
        for (blk, _port, _reader) in self._sources:
            if blk.net is not src_block0.net:
                for n in blk._all_nodes:
                    src_block0.net.add_node(n)
                blk.net = src_block0.net

        # criar nó-ponte (operation vindo do bloco da 1ª origem)
        op_node = WiringNode(
            node_id=f"bridge_multi__to__{dest_block.block_id}_{dest_port}_{dest_attr}",
            operation=src_block0.build_bridge_operation(to_attr=dest_attr, func=self._f_multi),
        )
        g = src_block0.net
        g.add_node(op_node)

        # conectar TODAS as origens ao bridge, na mesma ordem de _sources
        # e o bridge ao destino .in
        for (blk, port, _reader) in self._sources:
            g.connect(blk.port(port), op_node)

        if dest_block.net is not g:
            # adota o destino na mesma rede (por segurança)
            for n in dest_block._all_nodes:
                g.add_node(n)
            dest_block.net = g

        g.connect(op_node, dest_block.port("in"))
        return dest_field


class FieldRef:
    """
    (block, port, attr). Pode:
      - ligar diretamente com '>>' (identidade)
      - virar Expr com '_as_expr' e participar de fórmulas
    """
    def __init__(self, owner_block: "BlockWithSchema", port: str, attr: str):
        self._owner = owner_block
        self._port = port
        self._attr = attr

    def __rshift__(self, other: "FieldRef"):
        # identidade: f(inputs[0]) = reader(inputs[0])
        reader = self._owner.get_reader(self._port, self._attr)
        e = Expr([(self._owner, self._port, reader)], lambda inputs: float(reader(inputs[0])))
        return e >> other

    def _as_expr(self) -> Expr:
        reader = self._owner.get_reader(self._port, self._attr)
        return Expr([(self._owner, self._port, reader)], lambda inputs: float(reader(inputs[0])))

    # aritmética vira Expr multi-origem ao combinar
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
    """Expose campos definidos no schema do bloco."""
    def __init__(self, owner_block: "BlockWithSchema", port: str):
        self._owner = owner_block
        self._port = port

    def __getattr__(self, attr: str) -> FieldRef:
        if not self._owner.has_attr(self._port, attr):
            raise AttributeError(f"Porta '{self._port}' não tem campo '{attr}' neste bloco.")
        return FieldRef(self._owner, self._port, attr)
