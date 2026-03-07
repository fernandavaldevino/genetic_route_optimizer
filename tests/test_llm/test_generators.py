"""
Testes para geradores de conteúdo
"""

from src.core.service_points import create_service_point
from src.llm.generators import ManualGenerator, RouteGenerator, QASystem
import pytest


# Mock de provedor para testes
class MockLLMProvider:
    """ Provedor mock para testes sem chamar API real """
    
    def __init__(self):
        self.api_key = "mock"
        self.model = "mock"
        self.temperature = 0.7
    
    def generate_text(self, prompt, max_tokens=None, system_message=None):
        return "Mock manual de instruções com preparação, instruções e contatos de emergência."
    
    def generate_chat_response(self, messages, max_tokens=None):
        return "Mock resposta de chat."
    
    def validate_connection(self):
        return True


@pytest.fixture
def sample_route():
    """ Cria rota de exemplo para testes """
    return [
        create_service_point(0, (0, 0), 'regular'),  # Depósito
        create_service_point(1, (10, 10), 'emergency'),
        create_service_point(2, (20, 20), 'medication'),
        create_service_point(3, (30, 30), 'postpartum'),
    ]


def test_manual_generator(sample_route):
    """ Testa geração de manual """
    provider = MockLLMProvider()
    generator = ManualGenerator(provider)
    
    manual = generator.generate_manual(sample_route)
    
    assert isinstance(manual, str)
    assert len(manual) > 0


def test_route_generator(sample_route):
    """ Testa geração de roteiro """
    provider = MockLLMProvider()
    generator = RouteGenerator(provider)
    
    roteiro = generator.generate_route_description(sample_route)
    
    assert isinstance(roteiro, str)
    assert len(roteiro) > 0


def test_qa_system(sample_route):
    """ Testa sistema de Q&A """
    provider = MockLLMProvider()
    qa = QASystem(provider)
    
    # Define rota
    qa.set_route(sample_route)
    assert qa.route_context is not None
    
    # Faz pergunta
    resposta = qa.ask("Quantas paradas temos?")
    assert isinstance(resposta, str)
    
    # Verifica histórico
    history = qa.get_conversation_history()
    assert len(history) == 1
    
    # Limpa histórico
    qa.clear_history()
    assert len(qa.get_conversation_history()) == 0
