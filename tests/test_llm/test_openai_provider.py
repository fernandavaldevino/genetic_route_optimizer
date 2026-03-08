""" Testes para o provedor OpenAI usando pytest 

Markers:
@pytest.fixture: Permite criar funções que configuram o ambiente de teste e podem ser reutilizadas em vários testes.
@pytest.mark.integration: São "testes de integração" que precisam de conexão real com a API (custam dinheiro/tokens).
    - Para executar apenas estes testes: pytest -m integration
    - Para pular estes testes: pytest -m "not integration"
@pytest.mark.parametrize: Permite executar o mesmo teste múltiplas vezes com diferentes conjuntos de parâmetros.
@pytest.mark.llm: São "testes relacionados a provedores LLM".

"""

import pytest
import os
from dotenv import load_dotenv

from src.llm.providers.openai_provider import OpenAIProvider


# Carrega variáveis de ambiente (.env)
load_dotenv()


@pytest.fixture
def api_credentials():
    """ Fixture que carrega as credenciais da API do .env """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    if not api_key:
        pytest.skip("OPENAI_API_KEY não configurada no .env")
    
    return {
        "api_key": api_key,
        "model": model
    }


@pytest.fixture
def openai_provider(api_credentials):
    """ Fixture que cria um provedor OpenAI real para testes de integração """
    return OpenAIProvider(
        api_key=api_credentials["api_key"],
        model=api_credentials["model"],
        temperature=0.7
    )


class TestOpenAIProviderBasic:
    """ Classe com testes básicos do OpenAIProvider """
    
    def test_provider_initialization(self, api_credentials):
        """Testa se o provedor é criado corretamente"""
        provider = OpenAIProvider(
            api_key=api_credentials["api_key"],
            model=api_credentials["model"],
            temperature=0.7
        )
        
        # Verifica se os atributos foram configurados corretamente
        assert provider.api_key == api_credentials["api_key"]
        assert provider.model == api_credentials["model"]
        assert provider.temperature == 0.7
        assert provider.client is not None
    
    def test_provider_with_different_temperature(self, api_credentials):
        """Testa criação do provedor com temperatura diferente"""
        provider = OpenAIProvider(
            api_key=api_credentials["api_key"],
            model=api_credentials["model"],
            temperature=0.5
        )
        
        assert provider.temperature == 0.5


@pytest.mark.integration
class TestOpenAIProviderConnection:
    """ Classe com testes de conexão com a API OpenAI """
    
    def test_validate_connection(self, openai_provider):
        """Testa se a conexão com a API OpenAI está funcionando"""
        result = openai_provider.validate_connection()
        
        # Verifica se a conexão foi validada com sucesso
        assert result is True, "Falha ao validar conexão com OpenAI"
    

    def test_generate_simple_text(self, openai_provider):
        """ Testa geração de texto simples """
        response = openai_provider.generate_text(
            prompt='Diga apenas "Olá"',
            max_tokens=10
        )
        
        # Verifica se recebeu uma resposta válida
        assert response is not None
        assert len(response) > 0
        assert isinstance(response, str)
    

    def test_generate_text_with_system_message(self, openai_provider):
        """ Testa geração de texto com mensagem de sistema """
        response = openai_provider.generate_text(
            prompt='Qual é 2+2?',
            max_tokens=20,
            system_message="Você é uma calculadora. Responda apenas com números."
        )
        
        # Verifica se recebeu uma resposta
        assert response is not None
        assert len(response) > 0
        # Verifica se a resposta contém "4"
        assert "4" in response
    

    def test_generate_chat_response(self, openai_provider):
        """ Testa geração de resposta de chat """
        messages = [
            {"role": "system", "content": "Você é um assistente útil"},
            {"role": "user", "content": "Qual é a capital do Brasil?"}
        ]
        
        response = openai_provider.generate_chat_response(
            messages=messages,
            max_tokens=50
        )
        
        # Verifica se recebeu uma resposta válida
        assert response is not None
        assert len(response) > 0
        # Verifica se menciona Brasília
        assert "Brasília" in response or "brasília" in response.lower()
    

    def test_generate_text_portuguese(self, openai_provider):
        """ Testa geração de texto em português """
        response = openai_provider.generate_text(
            prompt='Diga "Hello, world!" em português',
            max_tokens=50
        )
        
        # Verifica se a resposta está em português
        assert response is not None
        assert "Olá" in response or "olá" in response.lower() or "mundo" in response.lower()


@pytest.mark.integration
class TestOpenAIProviderErrors:
    """ Classe com testes de tratamento de erros"""
    
    def test_invalid_api_key(self):
        """ Testa comportamento com API key inválida - Deve retornar False """
        provider = OpenAIProvider(
            api_key="sk-invalid-key-123",
            model="gpt-3.5-turbo"
        )
        result = provider.validate_connection()
        assert result is False
    
    def test_generate_text_with_invalid_key(self):
        """ Testa geração de texto com chave inválida - Deve lançar RuntimeError """
        provider = OpenAIProvider(
            api_key="sk-invalid-key-123",
            model="gpt-3.5-turbo"
        )
        with pytest.raises(RuntimeError) as exc_info:
            provider.generate_text(prompt="Teste")
        
        assert "Erro ao gerar texto" in str(exc_info.value)


# Testes parametrizados - executa o mesmo teste com valores diferentes
@pytest.mark.parametrize("temperature,expected", [
    (0.0, 0.0),
    (0.5, 0.5),
    (0.7, 0.7),
    (1.0, 1.0),
])
def test_temperature_values(api_credentials, temperature, expected):
    """ Testa diferentes valores de temperatura """
    provider = OpenAIProvider(
        api_key=api_credentials["api_key"],
        model=api_credentials["model"],
        temperature=temperature
    )
    assert provider.temperature == expected


@pytest.mark.parametrize("model", [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo",
])
def test_different_models(api_credentials, model):
    """ Testa criação do provedor com diferentes modelos """
    provider = OpenAIProvider(
        api_key=api_credentials["api_key"],
        model=model,
        temperature=0.7
    )    
    assert provider.model == model
