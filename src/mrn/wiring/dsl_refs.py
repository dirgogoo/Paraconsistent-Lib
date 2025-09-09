# mrn/wiring/dsl_refs.py
from __future__ import annotations
from typing import Callable, List, Tuple, TYPE_CHECKING
from mrn.core.graph import Connection
if TYPE_CHECKING:
    from mrn.core.block_base import BlockWithSchema

Origin = Tuple["BlockWithSchema", str, Callable[[object], float]]

class Expr:
    def __init__(self, sources: List[Origin], f_multi: Callable[[List[object]], float]):
        self._sources = sources
        self._f_multi = f_multi

    @staticmethod
    def _ensure_expr(x) -> "Expr | None":
        if isinstance(x, Expr): return x
        if isinstance(x, FieldRef): return x._as_expr()
        return None

    @staticmethod
    def _combine(a: "Expr", b: "Expr", op: Callable[[float, float], float]) -> "Expr":
        len_a = len(a._sources); len_b = len(b._sources)
        sources = a._sources + b._sources
        def f_multi(inputs: List[object]) -> float:
            va = a._f_multi(inputs[:len_a])
            vb = b._f_multi(inputs[len_a:len_a+len_b])
            return op(va, vb)
        return Expr(sources, f_multi)

    def _combine_const(self, c: float, op, swap=False) -> "Expr":
        const_expr = Expr([], lambda _: float(c))
        return Expr._combine(const_expr, self, op) if swap else Expr._combine(self, const_expr, op)

    # aritmética (com coerção FieldRef → Expr)
    def __add__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(self, e, lambda a,b:a+b) if e else self._combine_const(float(other), lambda a,b:a+b)
    def __radd__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(e, self, lambda a,b:a+b) if e else self._combine_const(float(other), lambda a,b:a+b, swap=True)

    def __sub__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(self, e, lambda a,b:a-b) if e else self._combine_const(float(other), lambda a,b:a-b)
    def __rsub__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(e, self, lambda a,b:a-b) if e else self._combine_const(float(other), lambda a,b:a-b, swap=True)

    def __mul__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(self, e, lambda a,b:a*b) if e else self._combine_const(float(other), lambda a,b:a*b)
    def __rmul__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(e, self, lambda a,b:a*b) if e else self._combine_const(float(other), lambda a,b:a*b, swap=True)

    def __truediv__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(self, e, lambda a,b:a/b) if e else self._combine_const(float(other), lambda a,b:a/b)
    def __rtruediv__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(e, self, lambda a,b:a/b) if e else self._combine_const(float(other), lambda a,b:a/b, swap=True)

    def __pow__(self, other):
        e = Expr._ensure_expr(other)
        return Expr._combine(self, e, lambda a,b:a**b) if e else self._combine_const(float(other), lambda a,b:a**b)

    def __neg__(self): return Expr(self._sources, lambda inputs: -self._f_multi(inputs))
    def __abs__(self): return Expr(self._sources, lambda inputs: abs(self._f_multi(inputs)))

    # Conectar: REGISTRA Connection no BlockGraph (não cria nó)
    def __rshift__(self, dest_field: "FieldRef"):
        dest_block, dest_attr = dest_field._owner, dest_field._attr

        if not self._sources:
            raise RuntimeError("Expressão sem origens. Use ao menos um FieldRef.")

        graph = self._sources[0][0]._graph
        if graph is None:
            raise RuntimeError("Origem não está em um BlockGraph. Use graph.add_block(...) antes de conectar.")

        # guard simples contra ciclo direto
        for (blk, _p, _r) in self._sources:
            if blk is dest_block:
                raise ValueError("Conexão criaria ciclo (mesmo bloco). Use Delay/Memória.")

        graph.add_connection(Connection(self._sources, self._f_multi, dest_block, dest_attr))
        return dest_field


class FieldRef:
    def __init__(self, owner_block: "BlockWithSchema", port: str, attr: str):
        self._owner = owner_block
        self._port = port
        self._attr = attr

    def __rshift__(self, other: "FieldRef"):
        reader = self._owner.reader(self._port, self._attr)
        e = Expr([(self._owner, self._port, reader)], lambda inputs: float(reader(inputs[0])))
        return e >> other

    def _as_expr(self) -> Expr:
        reader = self._owner.reader(self._port, self._attr)
        return Expr([(self._owner, self._port, reader)], lambda inputs: float(reader(inputs[0])))

    # delega aritmética para Expr
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
    def __init__(self, owner_block, port: str):
        object.__setattr__(self, "_owner", owner_block)
        object.__setattr__(self, "_port", port)

    def __getattr__(self, attr: str) -> FieldRef:
        if not self._owner.has_attr(self._port, attr):
            raise AttributeError(
                f"Porta '{self._port}' não tem campo '{attr}' no bloco '{self._owner.block_id}'."
            )
        return FieldRef(self._owner, self._port, attr)

    def __setattr__(self, attr: str, value):
        if attr in ("_owner", "_port"):
            object.__setattr__(self, attr, value)
            return

        if not self._owner.has_attr(self._port, attr):
            raise AttributeError(
                f"Porta '{self._port}' não tem campo '{attr}' no bloco '{self._owner.block_id}'."
            )

        # só permite escrita na porta de entrada
        if self._port not in ("in", "input"):
            raise AttributeError(
                f"Campos de '{self._port}' são somente leitura. "
                f"Use bX.input.mu / bX.input.lam para setar entradas."
            )

        v = float(value)
        if attr == "mu":
            self._owner.set_input(mu=v)
        elif attr in ("lam", "lambda"):
            self._owner.set_input(lam=v)
        else:
            # se algum dia a porta "in" tiver outros campos
            self._owner.set_input(**{attr: v})

    def __call__(self, **kwargs):
        # ex.: b1.input(mu=0.6, lam=0.2)
        if self._port not in ("in", "input"):
            raise AttributeError("Somente a porta de entrada aceita escrita direta.")
        mu = kwargs.get("mu", kwargs.get("MU"))
        lam = kwargs.get("lam", kwargs.get("lambda"))
        self._owner.set_input(mu=mu, lam=lam)
        return self
    # ... (demais imports e classes)

class ConfigRef:
    """Permite b1.config.FL = 0.9, b1.config.FtC = 0.45, etc."""
    def __init__(self, owner_block):
        object.__setattr__(self, "_owner", owner_block)

    def __setattr__(self, name, value):
        # delega para set_params do bloco (invalida caches)
        self._owner.set_params(**{name: value})

    def __getattr__(self, name):
        # leitura direta (ex.: print(b1.config.FL))
        return getattr(self._owner, name)



