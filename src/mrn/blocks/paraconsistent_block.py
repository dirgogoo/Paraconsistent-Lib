# mrn/blocks/paraconsistent_block.py
from __future__ import annotations
from typing import Optional, Dict, Any, List, Callable
from mrn.wiring.block_with_schema import BlockWithSchema
# from mrn.nodes.wiring_node import WiringNode  # <- pode remover, não está sendo usado
from mrn.core.network_manager import Network_Manager
from mrn.core.isignal import ISignal
from mrn.core.inetwork_node import INetworkNode

from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal
from mrn.builders.input_node_builder import InputNodeBuilder
from mrn.presets.paraconsistent_classifier_output_node import ParaconsistentClassifierOutputNode
from mrn.presets.paraconsistent_parser_logic_node import ParaconsistentParserLogicNode
from mrn.presets.get_last_signal_logic_node import GetLastSignalLogicNode


class ParaconsistentBlock(BlockWithSchema):
    """
    Entradas/Saídas (schema do DSL):
      in:        { mu, lam }             -> SimpleParaconsistentSignal
      complete:  { mu, lam|lambda, gc|certainty, gct, gcr, mer, phie }
      classified:{ confidence }          -> (vindo do classificador)
    Internamente:
      InputNode -> GetLast -> ParserPreset -> ClassifierPreset
    """
    def __init__(
        self, *,
        block_id: str = "PC",
        network: Optional[Network_Manager] = None,
        initial_mu: Optional[float] = None,
        initial_lam: Optional[float] = None,
        source_id: str = "",
        # >>> limiares do classificador (passados só no init)
        tC: float = 0.30,
        tCT: float = 0.30,
        tD: float = 0.20,
        L: float = 0.05,
        nd: int = 3,
    ):
        super().__init__(block_id=block_id, network=network)

        # Nós reais do seu MRN
        self.n_in: INetworkNode       = InputNodeBuilder().build()
        self.n_getlast: INetworkNode  = GetLastSignalLogicNode()
        self.n_parser: INetworkNode   = ParaconsistentParserLogicNode()
        self.n_classifier: INetworkNode = ParaconsistentClassifierOutputNode(
            tC=tC, tCT=tCT, tD=tD, L=L, nd=nd
        )

        self._register_nodes(self.n_in, self.n_getlast, self.n_parser, self.n_classifier)
        self.net.connect(self.n_in,      self.n_getlast)  # input -> getLast
        self.net.connect(self.n_getlast, self.n_parser)   # getLast -> parser
        self.net.connect(self.n_parser,  self.n_classifier)

        # Schema do DSL (readers de float)
        self._io_schema = {
            "in": {
                "mu":  lambda s: float(getattr(s, "mu", 0.0)),
                "lam": lambda s: float(getattr(s, "lam", getattr(s, "lambda", 0.0))),
            },
            "complete": {
                "mu":  lambda s: float(getattr(s, "mu", 0.0)),
                "lam": lambda s: float(getattr(s, "lam", getattr(s, "lambda", 0.0))),
                "gc":  lambda s: float(getattr(s, "gc", getattr(s, "certainty", 0.0))),
                "gct": lambda s: float(getattr(s, "gct", 0.0)),
                "gcr": lambda s: float(getattr(s, "gcr", 0.0)),
                "mer": lambda s: float(getattr(s, "mer", 0.0)),
                "phie":lambda s: float(getattr(s, "phie", 0.0)),
                "certainty": lambda s: float(getattr(s, "certainty", getattr(s, "gc", 0.0))),
            },
            "classified": {
                "confidence": lambda s: float(getattr(s, "confidence", 0.0)),
            },
        }

        if initial_mu is not None and initial_lam is not None:
            self.set_input(initial_mu, initial_lam, source_id)

    # mapeia portas do DSL para nós reais
    def port(self, name: str) -> INetworkNode:
        name = name.lower()
        if name in ("in", "input"):         return self.n_in
        if name == "complete":               return self.n_parser
        if name in ("classified", "class"):  return self.n_classifier
        raise ValueError(f"Porta desconhecida: {name}")

    # ponte Expr(float) -> SimpleParaconsistentSignal (preservando o outro campo)
    def build_bridge_operation(self, *, to_attr: str, func: Callable):
        """
        Retorna um callable(List[ISignal]) -> List[ISignal] que:
        - se 'func' aceitar lista de sinais (multi-entrada), produz UM sinal de saída
        - se 'func' aceitar 1 sinal (single-entrada), mapeia cada input para um output
        """
        def op(signals: List[ISignal]) -> List[ISignal]:
            if not signals:
                return []

            # TENTATIVA 1: tratar como função multi-entrada (Expr com N origens)
            try:
                val_multi = func(signals)  # espera func(inputs: List[ISignal]) -> float
                val_multi = float(val_multi)

                # decide mu/lam do output único
                src = getattr(signals[0], "source_id", getattr(signals[0], "source", ""))
                if to_attr == "mu":
                    out = SimpleParaconsistentSignal(mu=val_multi, lam=0.0, source_id=src)
                else:
                    out = SimpleParaconsistentSignal(mu=0.0, lam=val_multi, source_id=src)
                return [out]

            except TypeError:
                # TENTATIVA 2: tratar como função single-entrada (retrocompatibilidade)
                outs: List[ISignal] = []
                for s in signals:
                    val = float(func(s))  # espera func(signal: ISignal) -> float
                    cur_mu  = float(getattr(s, "mu", 0.0))
                    cur_lam = float(getattr(s, "lam", getattr(s, "lambda", 0.0)))
                    src     = getattr(s, "source_id", getattr(s, "source", ""))

                    if to_attr == "mu":
                        new_mu, new_lam = val, cur_lam
                    else:
                        new_mu, new_lam = cur_mu, val

                    outs.append(SimpleParaconsistentSignal(mu=new_mu, lam=new_lam, source_id=src))
                return outs

        return op

    # conveniência
    def set_input(self, mu: float, lam: float, source_id: str = "") -> "ParaconsistentBlock":
        self.n_in.receive(SimpleParaconsistentSignal(mu, lam, source_id))
        return self

    def run(self):  # dispara a rede existente
        self.net.propagate_all()

    def get_complete(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.net.get_outputs(self.n_parser)]

    def get_classified(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.net.get_outputs(self.n_classifier)]
