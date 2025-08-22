# mrn/core/icalculation.py
from abc import ABC, abstractmethod
from .isignal import ISignal

class ICalculation(ABC):
    @abstractmethod
    def process(self, signal: ISignal) -> "ICalculation":
        """
        Processa o sinal e armazena internamente. Use result() para obter a saída.
        """
        pass

    def result(self) -> ISignal | None:
        """
        Retorna o resultado acumulado ou calculado com base nos sinais processados.
        """
        return None

