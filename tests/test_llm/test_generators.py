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
        # Detecta tipo de conteúdo pelo system_message ou prompt
        # Verifica se é geração de manual (verifica system_message E prompt)
        if (system_message and 'manual' in system_message.lower()) or \
           (prompt and 'manual de instruções' in prompt.lower()):
            # Retorna manual mock com seções obrigatórias
            return """# MANUAL DE INSTRUÇÕES PARA EQUIPE DE TRANSPORTE

## PREPARAÇÃO E CHECKLIST
- Verificar veículo abastecido e em boas condições
- Conferir documentação necessária
- Preparar materiais e equipamentos de segurança
- Verificar caixa térmica e controle de temperatura

## INSTRUÇÕES E PROCEDIMENTOS
1. Seguir a ordem de paradas conforme roteiro
2. Verificar protocolos especiais para cada tipo de atendimento
3. Manter controle de temperatura quando necessário
4. Registrar horários de chegada e saída

## CONTATOS DE EMERGÊNCIA
- Central de Operações: (11) 1234-5678
- Suporte Técnico: (11) 8765-4321
- Emergências Médicas: 192
"""
        # Verifica se é geração de roteiro
        elif (prompt and 'roteiro' in prompt.lower()) or \
             (prompt and 'sequência' in prompt.lower()):
            # Retorna roteiro mock com menções de paradas
            return """# ROTEIRO DE VISITAS

## Sequência de Atendimentos

Parada 1: Ponto de Atendimento Emergencial
- Horário previsto: 08:00
- Tipo: Atendimento de emergência
- Observações: Prioridade alta

Parada 2: Ponto de Medicação
- Horário previsto: 09:00
- Tipo: Entrega de medicamentos
- Observações: Controle de temperatura necessário

Parada 3: Ponto Pós-Parto
- Horário previsto: 10:00
- Tipo: Atendimento pós-parto
- Observações: Cuidados especiais
"""
        else:
            # Resposta genérica para outros casos
            return "Mock manual de instruções com preparação, instruções e contatos de emergência."
    
    def generate_chat_response(self, messages, max_tokens=None):
        return "Mock resposta de chat com informações sobre a rota e atendimentos."
    
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
