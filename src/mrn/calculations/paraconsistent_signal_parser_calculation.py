from mrn.core.ilogic_calculation import ICalculation
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal
from mrn.signals.complete_paraconsistent_signal import CompleteParaconsistentSignal

class ParaconsistentSignalParser(ICalculation):
    def process(self, signal: SimpleParaconsistentSignal) -> CompleteParaconsistentSignal:
        mu, lam = signal.mu, signal.lam

        gc = mu - lam
        gct = mu + lam - 1

        d = ((1 - abs(gc)) ** 2 + gct ** 2) ** 0.5
        gcr = 1 - d if gc >= 0 else d - 1

        mer = (gcr + 1) / 2
        phie = 1 - abs(2 * ((gct + 1) / 2) - 1)

        return CompleteParaconsistentSignal(mu, lam, gc, gct, gcr, mer, phie)