from mrn.core.icalculation import ICalculation
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal

class SimpleToCompleteParaconsistentCalculation(ICalculation):
    def __init__(self):
        self._last_result = None

    def process(self, signal: SimpleParaconsistentSignal) -> "SimpleToCompleteParaconsistentCalculation":
        mu, lam = signal.mu, signal.lam
        gc = mu - lam
        gct = mu + lam - 1
        d = ((1 - abs(gc)) ** 2 + gct ** 2) ** 0.5
        gcr = 1 - d if gc >= 0 else d - 1
        mer = (gcr + 1) / 2
        phie = 1 - abs(2 * ((gct + 1) / 2) - 1)

        self._last_result = CompleteParaconsistentSignal(mu, lam, gc, gct, gcr, mer, phie)
        return self

    def result(self) -> CompleteParaconsistentSignal:
        return self._last_result