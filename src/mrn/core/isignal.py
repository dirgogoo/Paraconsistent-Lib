from abc import ABC, abstractmethod
from typing import Any, Dict

class ISignal(ABC):
    @abstractmethod
    def get_certainty(self) -> float:
        """Retorna o grau de certeza ou valor interpretável para propagação."""
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Retorna se o sinal está vazio ou inválido."""
        pass

    @abstractmethod
    def clone(self) -> "ISignal":
        """Cria uma cópia do sinal para evitar efeitos colaterais."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Converte os dados do sinal para dicionário (para debug, logs, etc)."""
        pass