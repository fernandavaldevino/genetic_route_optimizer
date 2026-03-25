""" Provedor Ollama para modelos locais de LLM """

from dataclasses import dataclass
from typing import Dict, List, Optional
from .base import BaseLLMProvider

import ollama


@dataclass
class OllamaProvider(BaseLLMProvider):
    """ Provedor LLM utilizando Ollama para modelos locais """
    
    api_key: str = "not-needed"                 # Ollama não precisa de API key
    model: str = "llama2"
    temperature: float = 0.7
    base_url: str = "http://localhost:11434"    # URL padrão do Ollama


    def __post_init__(self):
        self.client = ollama.Client(host=self.base_url)

    
    def generate_text(self,
                      prompt: str,
                      max_tokens: Optional[int] = None,
                      system_message: Optional[str] = None) -> str:
        """ Gera texto com base no prompt fornecido """
        # Monta lista de mensagens para o chat
        messages = []
        
        # Adiciona mensagem do sistema, se fornecida
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Adiciona prompt do usuário
        messages.append({"role": "user", "content": prompt})
        
        # Chama Ollama
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": max_tokens if max_tokens else -1
                }
            )
            # Extrai o conteúdo da resposta
            return response['message']['content'].strip()
        
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar texto com Ollama: {str(e)}")
    

    def generate_chat_response(self,
                               messages,
                               max_tokens: Optional[int] = None) -> str:
        """ Gera resposta em formato de chat """
        try:
            response = self.client.chat(
                model = self.model,
                messages = messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": max_tokens if max_tokens else -1
                }
            )
            # Extrai o conteúdo da resposta
            return response['message']['content'].strip()
        
        except Exception as e:
            raise RuntimeError(f"Erro ao gerar resposta de chat com Ollama: {str(e)}")
        

    def validate_connection(self):
        """ Valida a conexão com o Ollama """
        try:
            # Tenta listar os modelos disponíveis
            models_response = self.client.list()

            # Compatível com diferentes versões da biblioteca ollama
            if hasattr(models_response, 'models'):
                # Versão mais recente: objeto ListResponse
                available_models = [m.model for m in models_response.models]
            elif isinstance(models_response, dict):
                # Versão antiga: dicionário
                available_models = [m.get('model', m.get('name', '')) for m in models_response.get('models', [])]
            else:
                # Fallback: tentar converter para lista
                available_models = []
            
            # Aceita tanto "llama2" quanto "llama2:latest"
            model_found = self.model in available_models or f"{self.model}:latest" in available_models
            
            if not model_found:
                print(f"Modelo '{self.model}' não encontrado.")
                print(f"Modelos disponíveis: {available_models}")
                print(f"Execute: ollama pull {self.model}")
                return False
            return True
        except Exception as e:
            print(f"Erro ao conectar com Ollama: {str(e)}")
            print(f"""# Instalar Ollama: curl -fsSL https://ollama.com/install.sh | sh
# Baixar modelo: ollama pull llama2
# Iniciar servidor: ollama serve""")
            return False
