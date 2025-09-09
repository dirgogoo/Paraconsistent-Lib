# mrn/paraconsistent/block.py
from __future__ import annotations
from typing import Any, Dict, Callable, Optional
import math

# -------------------------------
# Utilidades
# -------------------------------
def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def sgn(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


# -------------------------------
# Bloco Paraconsistente (LPA2v)
# -------------------------------
class ParaconsistentBlock:
    """
    Bloco paraconsistente (LPA2v) com suporte aos parâmetros:

    Parâmetros de entrada/config:
      - FL   : Learning Factor (0..1) — intensidade de ajustes de "vetor de suporte"
      - FtC  : Fator de Tolerância à Certeza (|GC| menor que isso é "suprimido")
      - FtCT : Fator de Tolerância à Contradição (|GCT| menor que isso é "suprimido")
      - FD   : Fator de Decisão (0..1) — “endurece” o limiar efetivo para decidir V/F
      - VSSC : Vetor de Suporte da Certeza (empurra μ' para cima/baixo)
      - VICC : Vetor de Suporte da Certeza “contrária” (empurra λ' para cima/baixo)
      - VSSCT: Vetor de Suporte da Contradição (empurra GCT)
      - VICCT: Vetor de Suporte da Contradição “contrária” (empurra GCT ao contrário)
      - VlV  : Viés (prior) pró-Verdadeiro (empurra decisão para V)
      - VlF  : Viés (prior) pró-Falso (empurra decisão para F)

    Colunas calculadas (equivalentes à sua tabela):
      FL, FtC, FD, VSSC, VICC, VSSCT, VICCT, VlV, VlF,
      μ’ (mu_p), λ’ (lam_p), μ, λ, GC, GCT, S1, d, D, GCR, φ,
      μE, μE’ (muE_p), μECT, μER, φE
      + rótulo (classe textual da região/decisão)

    Observações:
      - μ’ e λ’ (mu_p/lam_p) são versões ajustadas de μ, λ usando FL * VSS*.
      - GC, GCT são calculados com μ, λ originais (você pode mudar para μ’, λ’ se preferir).
      - S1 é um “grau resultante” após tolerância (aqui igual a GC_tolerado).
      - d e D: neste bloco usamos D = sqrt((1-|GC|)^2 + GCT^2) e d = |GC| (projeção simples).
      - GCR segue a clássica: 1 - D (GC≥0) ou D - 1 (GC<0).
      - φ = 1 - |GCT|; μE = (GC+1)/2; μECT = (GCT+1)/2; μER = (GCR+1)/2; φE = φ.
      - Decisão usa limiar efetivo: T_dec = FtC + FD*(1-FtC) e vieses (VlV, VlF).

    Você pode ajustar as regras de decisão/quase-regiões depois se quiser ficar
    mais fiel a um atlas específico de regiões do reticulado.
    """

    # ---- tipos leves (objetos de porta) ----
    class _InSig:    # usado em read_port("in")
        def __init__(self, mu: float, lam: float):
            self.mu = mu
            self.lam = lam
            


    class _CompleteSig:
        def __init__(self, d: Dict[str, float | str]):
            # expõe chaves como atributos
            for k, v in d.items(): setattr(self, k, v)

    class _ClassifiedSig:
        def __init__(self, label: str, confidence: float):
            self.label = label
            self.confidence = confidence

    # ---- construtor ----
    def __init__(self, block_id: str, *,
                 initial_mu=None, initial_lam=None,
                 FL=1.0, FtC=0.50, FtCT=None, FD=0.0,
                 VSSC=0.50, VICC=-0.50, VSSCT=0.50, VICCT=-0.50,
                 VlV=0.50, VlF=0.50, L=0.05):
        self.block_id = block_id
        self._mu_in = float(initial_mu) if initial_mu is not None else 0.0
        self._lam_in = float(initial_lam) if initial_lam is not None else 0.0

        # parâmetros configuráveis:
        self.FL   = float(FL)
        self.FtC  = float(FtC)
        self.FtCT = float(FtCT) if FtCT is not None else float(FtC)
        self.FD   = float(FD)

        self.VSSC  = float(VSSC)
        self.VICC  = float(VICC)
        self.VSSCT = float(VSSCT)
        self.VICCT = float(VICCT)

        self.VlV = float(VlV)
        self.VlF = float(VlF)
        self.L   = float(L)

        self._complete = None
        self._complete_dict = {}
        self._classified = None
        self._graph = None

        # schema (igual ao que você já tinha)
        self._schema = {
            "in": {
                "mu":  lambda s: float(getattr(s, "mu", 0.0)),
                "lam": lambda s: float(getattr(s, "lam", 0.0)),
            },
            "complete": {
                "mu":   lambda s: float(getattr(s, "μ", 0.0)),
                "lam":  lambda s: float(getattr(s, "λ", 0.0)),
                "gc":   lambda s: float(getattr(s, "GC", 0.0)),
                "gct":  lambda s: float(getattr(s, "GCT", 0.0)),
                "gcr":  lambda s: float(getattr(s, "GCR", 0.0)),
                "mer":  lambda s: float(getattr(s, "μER", 0.0)),
                "phie": lambda s: float(getattr(s, "φE", 0.0)),
                "mu_p":   lambda s: float(getattr(s, "μ’", 0.0)),
                "lam_p":  lambda s: float(getattr(s, "λ’", 0.0)),
                "s1":     lambda s: float(getattr(s, "S1", 0.0)),
                "d":      lambda s: float(getattr(s, "d", 0.0)),
                "D":      lambda s: float(getattr(s, "D", 0.0)),
                "phi":    lambda s: float(getattr(s, "φ", 0.0)),
                "muE":    lambda s: float(getattr(s, "μE", 0.0)),
                "muE_p":  lambda s: float(getattr(s, "μE’", 0.0)),
                "muECT":  lambda s: float(getattr(s, "μECT", 0.0)),
                "muER":   lambda s: float(getattr(s, "μER", 0.0)),
                "phiE":   lambda s: float(getattr(s, "φE", 0.0)),
            },
            "classified": {
                "confidence": lambda s: float(getattr(s, "confidence", 0.0))
            }
        }

        # grafo (injetado pelo runner / graph)
        self._graph = None

    # -------------------------------
    # API de bloco p/ DSL/Runner
    # -------------------------------

    def _invalidate(self):
        self._complete = None
        self._complete_dict = {}
        self._classified = None

    # ---- setters SEM pin (sobrescrevem sempre) ----
    def set_input(self, *, mu=None, lam=None):
        if mu is not None:
            self._mu_in = clamp01(float(mu))
        if lam is not None:
            self._lam_in = clamp01(float(lam))
        self._invalidate()

    def set_params(self, **kwargs):
        # permite alterar FL, FtC, FtCT, FD, VSSC, VICC, VSSCT, VICCT, VlV, VlF, L
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise AttributeError(f"Parâmetro inválido: {k}")
            setattr(self, k, float(v))
        self._invalidate()

    @property
    def config(self):
        # import tardio para evitar ciclos
        from mrn.wiring.dsl_refs import ConfigRef
        return ConfigRef(self)


    def has_attr(self, port: str, attr: str) -> bool:
        return port in self._schema and attr in self._schema[port]

    def reader(self, port: str, attr: str) -> Callable[[Any], float]:
        try:
            return self._schema[port][attr]
        except KeyError:
            raise AttributeError(f"Campo '{attr}' não existe na porta '{port}' do bloco '{self.block_id}'.")

    def read_port(self, name: str) -> Any:
        if name in ("in", "input"):
            return ParaconsistentBlock._InSig(self._mu_in, self._lam_in)
        if name == "complete":
            return self._as_complete_sig()
        if name in ("classified", "class"):
            return self._classified
        raise ValueError(f"Porta inexistente: {name}")

    # dentro do ParaconsistentBlock

    def merge_partial(self, attr: str, value: float) -> None:
        v = clamp01(float(value))
        if attr == "mu":
            self._mu_in = v
        elif attr in ("lam", "lambda"):
            self._lam_in = v
        else:
            raise ValueError(f"Attr inválido para entrada paraconsistente: {attr}")
        self._invalidate()


    # -------------------------------
    # Cálculo principal (compute)
    # -------------------------------
    def compute(self) -> None:
        mu = clamp01(self._mu_in)
        lam = clamp01(self._lam_in)

        # 1) Ajuste “aprendizado” nas entradas (μ’, λ’) usando vetores de suporte (VSS*)
        mu_p  = clamp01(mu  + self.FL * self.VSSC)
        lam_p = clamp01(lam + self.FL * self.VICC)

        # 2) Graus clássicos (usando μ, λ originais)
        GC  = mu - lam
        GCT = mu + lam - 1.0

        # 2.1) Ajuste adicional na contradição (aplica VSSCT/VICCT como viés no GCT)
        GCT_adj = GCT + self.FL * (self.VSSCT + self.VICCT) * 0.5
        # mantemos dentro de [-1,1] por segurança
        GCT_adj = max(-1.0, min(1.0, GCT_adj))

        # 3) Tolerâncias (FtC para GC; FtCT para GCT)
        GC_t  = GC  if abs(GC)  >= self.FtC  else 0.0
        GCT_t = GCT_adj if abs(GCT_adj) >= self.FtCT else 0.0

        # 4) S1 como “grau resultante de certeza” (simplificação comum: S1 := GC_t)
        S1 = GC_t

        # 5) Métricas geométricas padrão do reticulado
        # D (distância ao vértice “verdadeiro” ou “falso” via rotação paraconsistente)
        D = math.sqrt((1 - abs(GC))**2 + (GCT)**2)  # usando GC, GCT “puros” (você pode testar com ajustados)
        d = abs(GC)  # “projeção” simples na certeza (só informativo)

        # 6) Grau de Certeza Real (GCR) (conhecido na LPA2v)
        GCR = (1 - D) if GC >= 0 else (D - 1)

        # 7) Intervalos e evidências
        phi  = 1 - abs(GCT)             # φ (intervalo de certeza clássico)
        muE  = (GC + 1) / 2             # μE (grau de evidência)
        muE_p  = ((mu_p - lam_p) + 1) / 2     # μE’ (com entradas ajustadas)
        muECT  = (GCT + 1) / 2                # μECT (evidência “de contradição”)
        muER   = (GCR + 1) / 2                # μER (evidência “real”)
        phiE   = 1 - abs(GCT)                 # φE (= φ, mantido por compatibilidade)

        # 8) Decisão (rótulo) com limiar efetivo e vieses
        #    Limiar efetivo de decisão (endurecido por FD):
        T_dec = self.FtC + self.FD * (1.0 - self.FtC)  # cresce com FD; se FD=0 -> FtC
        #    Vieses: puxam GC para V/F
        GC_biased = GC + ( self.VlV if GC >= 0 else -self.VlF )

        label = self._decide_label(GC, GCT, GC_t, GCT_t, GC_biased, T_dec)

        # 9) Confiança para a classificação (exemplo simples)
        #    se estiver em V/F “forte”, confiança = |GC_biased| - T_dec; senão usa |GCT| - FtCT;
        #    se ficar abaixo de 0, usa L (mínimo).
        conf_vf  = max(abs(GC_biased) - T_dec, 0.0)
        conf_ct  = max(abs(GCT) - self.FtCT, 0.0)
        confidence = conf_vf if label in ("V", "F") else conf_ct
        if confidence == 0.0:
            confidence = self.L

        # 10) Preenche dicionário completo (sua tabela)
        cdict: Dict[str, float | str] = {
            # parâmetros “ecoando”
            "FL": self.FL, "FtC": self.FtC, "FD": self.FD,
            "VSSC": self.VSSC, "VICC": self.VICC, "VSSCT": self.VSSCT, "VICCT": self.VICCT,
            "VlV": self.VlV, "VlF": self.VlF,
            # entradas & ajustadas
            "μ’": mu_p, "λ’": lam_p, "μ": mu, "λ": lam,
            # graus/derivados
            "GC": GC, "GCT": GCT,
            "S1": S1, "d": d, "D": D, "GCR": GCR,
            "φ": phi,
            "μE": muE, "μE’": muE_p, "μECT": muECT, "μER": muER, "φE": phiE,
            # rótulo “curto” (também devolvido em classified)
            "label": label,
        }
        self._complete_dict = cdict
        self._complete = ParaconsistentBlock._CompleteSig(cdict)
        self._classified = ParaconsistentBlock._ClassifiedSig(label, float(confidence))

    # -------------------------------
    # Helpers de decisão/rotulagem
    # -------------------------------
    def _decide_label(
        self,
        GC: float,
        GCT: float,
        GC_t: float,
        GCT_t: float,
        GC_biased: float,
        T_dec: float
    ) -> str:
        """
        Heurística de rotulagem compatível com as “regiões” usuais do reticulado:
          V, F, ┬ (inconsistente), ┴ (indeterminado), Q-regiões e L/Indefinido.
        """
        # regiões “fortes” por decisão endurecida
        if GC_biased >= T_dec and abs(GCT) < self.FtCT:
            return "V"
        if GC_biased <= -T_dec and abs(GCT) < self.FtCT:
            return "F"
        if GCT >= self.FtCT and abs(GC) < self.FtC:
            return "┬"   # inconsistente
        if GCT <= -self.FtCT and abs(GC) < self.FtC:
            return "┴"   # indeterminado (paracompleto)

        # Quase-regiões, avaliando dominância relativa
        # centro: |GC| < FtC e |GCT| < FtCT
        in_center = (abs(GC) < self.FtC) and (abs(GCT) < self.FtCT)
        if in_center:
            # inclinações:
            if GC >= 0 and abs(GC) >= abs(GCT):
                return "QV→ ┬"   # Quase Verdadeiro tendendo Inconsistente
            if GC >= 0 and abs(GC) < abs(GCT):
                return "QV→ ┴"   # Quase Verdadeiro tendendo Indeterminado
            if GC < 0 and abs(GC) >= abs(GCT):
                return "QF→ ┬"   # Quase Falso tendendo a Inconsistente
            if GC < 0 and abs(GC) < abs(GCT):
                return "QF→ ┴"   # Quase Falso tendendo a Indeterminado
            return "I"           # indefinido

        # bordas intermediárias (GC e GCT não “fortes” o suficiente)
        if GC >= 0 and GCT >= 0:
            # Quase Inconsistente tendendo Verdadeiro vs Quase Verdadeiro tendendo Inconsistente
            return "Q┬ → V" if abs(GCT) >= abs(GC) else "Qv→ ┬"
        if GC >= 0 and GCT < 0:
            return "QV→ ┴" if abs(GC) >= abs(GCT) else "Q┴→V"
        if GC < 0 and GCT >= 0:
            return "Q┬ → F" if abs(GCT) >= abs(GC) else "QF→ ┬"
        if GC < 0 and GCT < 0:
            return "QF→ ┴" if abs(GC) >= abs(GCT) else "Q┴→F"

        return "I"

    # -------------------------------
    # Acessores convenientes p/ DSL
    # -------------------------------
    @property
    def input(self):
        # PortRef “lazy” para evitar import cíclico
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

    # -------------------------------
    # Helpers internos
    # -------------------------------
    def _as_complete_sig(self) -> _CompleteSig:
        if self._complete is None:
            self.compute()
        return self._complete
    
    def pin_input(self, *, mu: bool|None=None, lam: bool|None=None):
        if mu is not None:  self._pin["mu"] = bool(mu)
        if lam is not None: self._pin["lam"] = bool(lam)

    def unpin_all(self):
        self._pin["mu"] = False; self._pin["lam"] = False

