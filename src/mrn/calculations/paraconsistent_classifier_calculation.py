from __future__ import annotations
from mrn.core.icalculation import ICalculation
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal
from mrn.signals.classified_paraconsistent_signal import ClassifiedParaconsistentSignal

class ParaconsistentClassifierCalculation(ICalculation):
    """
    Classificador paraconsistente com limiares diretamente no __init__.
      tC  : limiar de certeza (|c| >= tC -> V/F)
      tCT : limiar de contradição (|ct| >= tCT -> C)
      tD  : faixa de dúvida (|ct| <= tD quando |c| < tC)
      L   : energia mínima (E=max(mu,lam); E < L -> 'L')
      nd  : casas decimais para arredondar confidence
    """
    def __init__(self, tC: float = 0.30, tCT: float = 0.30, tD: float = 0.20, L: float = 0.05, nd: int = 3):
        self.tC  = float(max(0.0, min(1.0, tC)))
        self.tCT = float(max(0.0, min(1.0, tCT)))
        self.tD  = float(max(0.0, min(1.0, tD)))
        self.L   = float(max(0.0, min(1.0, L)))
        self.nd  = int(max(0, nd))
        self._last = None

    # (opcional) ajuste em runtime
    def update_thresholds(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, float(v) if k != "nd" else int(v))
        self.tC  = max(0.0, min(1.0, self.tC))
        self.tCT = max(0.0, min(1.0, self.tCT))
        self.tD  = max(0.0, min(1.0, self.tD))
        self.L   = max(0.0, min(1.0, self.L))
        self.nd  = max(0, self.nd)

    @staticmethod
    def _r(x: float, nd: int) -> float:
        v = round(float(x), nd)
        return 0.0 if v == 0.0 else v

    def process(self, s: CompleteParaconsistentSignal) -> "ParaconsistentClassifierCalculation":
        mu  = float(getattr(s, "mu", 0.0))
        lam = float(getattr(s, "lam", getattr(s, "lambda", 0.0)))

        c   = mu - lam              # certeza
        ct  = mu + lam - 1.0        # contradição
        E   = max(mu, lam)          # energia mínima

        abs_c, abs_ct = abs(c), abs(ct)

        # 1) Baixa energia
        if E < self.L:
            label, conf = "L", max(self.L - E, 0.0)

        # 2) Contradição
        elif abs_ct >= self.tCT:
            label, conf = "C", max(abs_ct - self.tCT, 0.0)

        # 3) Decisão forte (V/F) com contradição controlada
        elif (abs_c >= self.tC) and (abs_ct <= self.tD):
            label = "V" if c > 0.0 else "F"
            conf  = max(abs_c - self.tC, 0.0)

        # 4) Dúvida
        else:
            label = "D"
            gaps = []
            if abs_c < self.tC:    gaps.append(self.tC - abs_c)
            if abs_ct > self.tD:   gaps.append(abs_ct - self.tD)
            if abs_ct < self.tCT:  gaps.append(self.tCT - abs_ct)
            conf = max(min(gaps) if gaps else 0.0, 0.0)

        conf = self._r(conf, self.nd)
        src  = getattr(s, "source_id", getattr(s, "source", ""))

        self._last = ClassifiedParaconsistentSignal(label=label, confidence=conf, source_id=src)
        return self

    def result(self) -> ClassifiedParaconsistentSignal:
        return self._last
