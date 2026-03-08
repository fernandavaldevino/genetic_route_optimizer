""" 
   Interface base para provedores de LLM. 
   Todos os provedores de LLM devem implementar esta interface para garantir a compatibilidade com o sistema. 
"""

from typing import Dict, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class BaseLLMProvider(ABC):
    api_key: str
    model: str
    temperature: float = 0.7

    @abstractmethod
    def generate_text(self,
                      prompt: str,
                      max_tokens: Optional[int] = 100,
                      **kwargs) -> str:
        """ Gera texto com base no prompt fornecido """
        pass

    @abstractmethod
    def generate_chat_response(self,
                               messages: List[Dict[str, str]],
                               max_tokens: Optional[int] = 100) -> str:
        """ Gera resposta de chat com base nas mensagens fornecidas """
        pass

    @abstractmethod
    def validate_connection(self) -> bool:
        """ Valida a conexão com o provedor de LLM """
        pass