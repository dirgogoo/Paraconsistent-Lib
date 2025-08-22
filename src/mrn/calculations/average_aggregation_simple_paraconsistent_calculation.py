from typing import List, Optional
from mrn.core.icalculation import ICalculation
from mrn.signals.simple_paraconsistent_signal import SimpleParaconsistentSignal

class AggregationSimpleParaconsistentCalculation(ICalculation):
    def __init__(self):
        self._signals: List[SimpleParaconsistentSignal] = []
        self._aggregated: Optional[SimpleParaconsistentSignal] = None

    def process(self, signal: SimpleParaconsistentSignal) -> "AggregationSimpleParaconsistentCalculation":
        print("Processing")
        self._signals.append(signal)
        return self

    def result(self) -> Optional[SimpleParaconsistentSignal]:
        if not self._signals:
            return None

        n = len(self._signals)
        avg_mu = sum(s.mu for s in self._signals) / n
        avg_lam = sum(s.lam for s in self._signals) / n

        self._aggregated = SimpleParaconsistentSignal(
            mu=avg_mu,
            lam=avg_lam,
            source_id="aggregated"
        )
        return self._aggregated
