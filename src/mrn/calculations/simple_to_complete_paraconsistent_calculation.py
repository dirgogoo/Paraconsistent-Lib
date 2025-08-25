from mrn.core.icalculation import ICalculation
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal

class SimpleToCompleteParaconsistentCalculation(ICalculation):
    def __init__(self, nd: int = 6, clamp: bool = True):
        """
        nd: casas decimais para arredondar a saída do cálculo.
        clamp: se True, normaliza campos para intervalos esperados.
        """
        self._last_result = None
        self.nd = int(nd)
        self.clamp = bool(clamp)

    # ----- helpers -----
    def _r(self, x: float) -> float:
        r = round(float(x), self.nd)
        # evita -0.0 em prints/logs
        return 0.0 if r == 0.0 else r

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(x)))

    # ----- cálculo principal -----
    def process(self, signal: SimpleParaconsistentSignal) -> "SimpleToCompleteParaconsistentCalculation":
        mu, lam = float(signal.mu), float(signal.lam)

        # métricas paraconsistentes
        gc  = mu - lam
        gct = mu + lam - 1.0
        d   = ((1.0 - abs(gc)) ** 2 + (gct ** 2)) ** 0.5
        gcr = (1.0 - d) if gc >= 0.0 else (d - 1.0)
        mer = (gcr + 1.0) / 2.0
        phie = 1.0 - abs(2.0 * ((gct + 1.0) / 2.0) - 1.0)

        if self.clamp:
            # intervalos típicos (ajuste se seu modelo exigir outros limites):
            gc   = self._clamp(gc,  -1.0, 1.0)
            gct  = self._clamp(gct, -1.0, 1.0)
            gcr  = self._clamp(gcr, -1.0, 1.0)
            mer  = self._clamp(mer,  0.0, 1.0)
            phie = self._clamp(phie, 0.0, 1.0)

        # arredonda tudo na **saída** do cálculo
        mu_r  = self._r(mu)
        lam_r = self._r(lam)
        gc_r  = self._r(gc)
        gct_r = self._r(gct)
        gcr_r = self._r(gcr)
        mer_r = self._r(mer)
        phie_r= self._r(phie)

        self._last_result = CompleteParaconsistentSignal(
            mu_r, lam_r, gc_r, gct_r, gcr_r, mer_r, phie_r
        )
        return self

    def result(self) -> CompleteParaconsistentSignal:
        return self._last_result
