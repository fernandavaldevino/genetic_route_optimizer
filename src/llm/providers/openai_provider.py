""" Provedor de LLM para OpenAI """

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from .base import BaseLLMProvider

import openai

@dataclass
class OpenAIProvider(BaseLLMProvider):
    api_key: str
    model: str
    temperature: float = 0.7
    client: openai.OpenAI = field(default=None, init=False, repr=False)

    def __post_init__(self):
        self.client = openai.OpenAI(api_key=self.api_key, timeout=30.0, max_retries=3)

    
    def generate_text(self, prompt: str, max_tokens: Optional[int] = None, system_message: Optional[str] = None) -> str:
        """ Gera texto com base no prompt fornecido """
        # Monta as mensagens para o chat
        messages = []

        # Adiciona as mensagens do sistema, se fornecidas
        if system_message:
            messages.append({"role": "system", "content": system_message})

        # Adiciona a mensagem (prompt) do usuário
        messages.append({"role": "user", "content": prompt})

        # Chama a API do OpenAI para gerar a resposta
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )

            # Extrai e retorna o conteúdo da resposta
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar texto: {str(e)}")
        
    
    def generate_chat_response(self, messages: List[Dict[str, str]], max_tokens: Optional[int] = None) -> str:
        """ Gera resposta de chat com base nas mensagens fornecidas """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content.strip()
        
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar resposta de chat: {str(e)}")
        

    def validate_connection(self) -> bool:
        """ Testa a conexão com a API do OpenAI """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": "Teste de conexão"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"Erro ao validar conexão: {str(e)}")
            return False