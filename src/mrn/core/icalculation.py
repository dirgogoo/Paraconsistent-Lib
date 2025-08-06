from abc import ABC, abstractmethod
from .isignal import ISignal

class ICalculation(ABC):
    @abstractmethod
    def process(self, signal: ISignal) -> ISignal:
        """
        Realiza o processamento lógico-matemático sobre um sinal.
        Pode retornar um novo sinal com dados enriquecidos.
        """
        pass