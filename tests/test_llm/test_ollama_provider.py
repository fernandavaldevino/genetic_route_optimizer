""" Testes para o provedor Ollama usando pytest 

Markers:
@pytest.fixture: Funções que configuram o ambiente de teste e podem ser reutilizadas em vários testes.
@pytest.mark.integration: São "testes de integração" que precisam de conexão real com o Ollama local.
    - Para executar apenas estes testes: pytest -m integration
    - Para pular estes testes: pytest -m "not integration"
@pytest.mark.parametrize: Permite executar o mesmo teste múltiplas vezes com diferentes conjuntos de parâmetros.
@pytest.mark.llm: São testes relacionados a provedores LLM.

IMPORTANTE: Para executar estes testes, você precisa ter o Ollama instalado e rodando localmente.
Verificar como instalar o Ollama em: https://ollama.ai
"""

import pytest
import os
from dotenv import load_dotenv

from src.llm.providers.ollama_provider import OllamaProvider


# Carrega variáveis de ambiente (.env)
load_dotenv()


@pytest.fixture
def ollama_config():
    """ Fixture que carrega as configurações do Ollama do .env """
    model = os.getenv("OLLAMA_MODEL", "llama2")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    return {
        "model": model,
        "base_url": base_url
    }


@pytest.fixture
def ollama_provider(ollama_config):
    """ Fixture que cria um provedor Ollama para testes """
    return OllamaProvider(
        model=ollama_config["model"],
        base_url=ollama_config["base_url"],
        temperature=0.7
    )


class TestOllamaProviderBasic:
    """ Classe com testes básicos do OllamaProvider """
    
    def test_provider_initialization(self, ollama_config):
        """ Testa se o provedor é criado corretamente """
        provider = OllamaProvider(
            model=ollama_config["model"],
            base_url=ollama_config["base_url"],
            temperature=0.7
        )
        
        # Verifica se os atributos foram configurados corretamente
        assert provider.model == ollama_config["model"]
        assert provider.base_url == ollama_config["base_url"]
        assert provider.temperature == 0.7
        assert provider.client is not None
    
    def test_provider_with_different_temperature(self, ollama_config):
        """ Testa criação do provedor com temperatura diferente """
        provider = OllamaProvider(
            model=ollama_config["model"],
            base_url=ollama_config["base_url"],
            temperature=0.5
        )
        
        assert provider.temperature == 0.5
    
    def test_provider_default_values(self):
        """ Testa valores padrão do provedor """
        provider = OllamaProvider()
        
        assert provider.model == "llama2"
        assert provider.base_url == "http://localhost:11434"
        assert provider.temperature == 0.7
        assert provider.api_key == "not-needed"


@pytest.mark.integration
class TestOllamaProviderConnection:
    """ Classe com testes de conexão com o Ollama local 
        O Ollama deve estar instalado e rodando!
    """
    
    def test_validate_connection(self, ollama_provider):
        """ Testa se a conexão com o Ollama está funcionando """
        result = ollama_provider.validate_connection()
        
        # Verifica se a conexão foi validada com sucesso
        assert result is True, "Falha ao validar conexão com Ollama. Certifique-se de que o Ollama está rodando."
    

    def test_generate_simple_text(self, ollama_provider):
        """ Testa geração de texto simples """
        response = ollama_provider.generate_text(
            prompt='Diga apenas "Olá"',
            max_tokens=10
        )
        
        # Verifica se recebeu uma resposta válida
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
        print(f"\n[DEBUG] Resposta recebida: {response}")
    

    def test_generate_text_with_system_message(self, ollama_provider):
        """ Testa geração de texto com mensagem de sistema """
        response = ollama_provider.generate_text(
            prompt='Qual é 2+2?',
            max_tokens=20,
            system_message="Você é uma calculadora. Responda apenas com números."
        )
        
        # Verifica se recebeu uma resposta
        assert response is not None
        assert len(response) > 0
        print(f"\n[DEBUG] Resposta recebida: {response}")
        # Verifica se a resposta contém "4"
        assert "4" in response
    

    def test_generate_chat_response(self, ollama_provider):
        """ Testa geração de resposta de chat """
        messages = [
            {"role": "system", "content": "Você é um assistente útil"},
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        response = ollama_provider.generate_chat_response(
            messages=messages,
            max_tokens=50
        )
        
        # Verifica se recebeu uma resposta válida
        assert response is not None
        assert len(response) > 0
        print(f"\n[DEBUG] Resposta recebida: {response}")
        # Verifica se menciona Brasília
        assert "Brasília" in response or "brasília" in response.lower()
    

    def test_generate_text_portuguese(self, ollama_provider):
        """ Testa geração de texto em português """
        response = ollama_provider.generate_text(
            prompt='Diga "Hello, world!" em português',
            max_tokens=50
        )
        
        # Verifica se a resposta está em português
        assert response is not None
        print(f"\n[DEBUG] Resposta recebida: {response}")
        assert "Olá" in response or "olá" in response.lower() or "mundo" in response.lower()


@pytest.mark.integration
class TestOllamaProviderErrors:
    """ Classe com testes de tratamento de erros """
    
    def test_invalid_base_url(self):
        """ Testa comportamento com URL inválida - Deve retornar False """
        provider = OllamaProvider(
            model="llama2",
            base_url="http://localhost:9999"  # Porta diferente (não em uso)
        )
        result = provider.validate_connection()
        assert result is False
    
    def test_generate_text_with_invalid_url(self):
        """ Testa geração de texto com URL inválida - Deve lançar RuntimeError """
        provider = OllamaProvider(
            model="llama2",
            base_url="http://localhost:9999"  # Porta diferente (não em uso)
        )
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate_text(prompt="Teste")
        
        assert "Erro ao gerar texto" in str(exc_info.value)


@pytest.mark.parametrize("temperature,expected", [
    (0.0, 0.0),
    (0.5, 0.5),
    (0.7, 0.7),
    (1.0, 1.0),
])
def test_temperature_values(ollama_config, temperature, expected):
    """ Testa diferentes valores de temperatura """
    provider = OllamaProvider(
        model=ollama_config["model"],
        base_url=ollama_config["base_url"],
        temperature=temperature
    )
    assert provider.temperature == expected


@pytest.mark.parametrize("model", [
    "llama2",
    "mistral",
    "codellama",
])
def test_different_models(ollama_config, model):
    """ Testa criação do provedor com diferentes modelos """
    provider = OllamaProvider(
        model=model,
        base_url=ollama_config["base_url"],
        temperature=0.7
    )    
    assert provider.model == model
