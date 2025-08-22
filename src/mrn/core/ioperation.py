from abc import ABC, abstractmethod
from typing import List
from mrn.core.isignal import ISignal

class IOperation(ABC):
    @abstractmethod
    def execute(self, inputs: List[ISignal]) -> List[ISignal]:
        """
        Executa a operação lógica com base em uma lista de sinais de entrada.

        :param inputs: Lista de ISignal recebidos pelo nó.
        :return: Lista de ISignal gerados como saída.
        """
        pass

    @abstractmethod
    def name(self) -> str:
        """
        Retorna o nome da operação (útil para debug, logs e visualizações).
        """
        pass
