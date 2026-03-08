"""
Testes para provedores de LLM
"""

import pytest
from src.llm.providers import create_llm_provider, get_available_providers


def test_get_available_providers():
    """ Testa listagem de provedores disponíveis """
    providers = get_available_providers()
    
    assert 'openai' in providers
    assert 'ollama' in providers
    assert providers['openai']['requires_api_key'] == True
    assert providers['ollama']['requires_api_key'] == False


def test_create_provider_invalid():
    """ Testa criação de provedor inválido """
    with pytest.raises(ValueError):
        create_llm_provider("invalid_provider")
