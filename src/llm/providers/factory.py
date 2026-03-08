""" Factory para criar provedores de LLM baseado em configuração """

from typing import Optional
from dotenv import load_dotenv
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .ollama_provider import OllamaProvider

import os


def create_llm_provider(provider_type: Optional[str] = None) -> BaseLLMProvider:
    """ Cria provedor de LLM baseado em configuração """
    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv()

    # Determina o provedor a ser usado
    if provider_type is None:
        provider_type = os.getenv("LLM_PROVIDER", "openai").lower()

    provider_type = provider_type.lower()

    # Cria provedor OpenAI
    if provider_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY não encontrada. Configure no arquivo .env")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

        return OpenAIProvider(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
    
    # Cria provedor Ollama
    elif provider_type == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama2")
        temperature = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
        
        provider = OllamaProvider(
            model=model,
            temperature=temperature,
            base_url=base_url
        )
        
        # Valida conexão
        if not provider.validate_connection():
            raise ValueError(
                f"Não foi possível conectar ao Ollama em {base_url}. "
                f"Certifique-se de que o servidor está rodando (ollama serve) "
                f"e o modelo '{model}' está instalado (ollama pull {model})."
            )
        return provider
    
    else:
        raise ValueError(
            f"Provedor '{provider_type}' não suportado. "
            f"Use 'openai' ou 'ollama'."
        )
    

def get_available_providers() -> dict:
    """ Retorna informações sobre provedores disponíveis """
    return {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
            "requires_api_key": True,
            "cost": "Pago (por token)",
            "privacy": "Dados enviados para OpenAI"
        },
        "ollama": {
            "name": "Ollama (Local)",
            "models": ["llama2", "mistral", "codellama", "neural-chat"],
            "requires_api_key": False,
            "cost": "Gratuito",
            "privacy": "Dados permanecem locais"
        }
    }
