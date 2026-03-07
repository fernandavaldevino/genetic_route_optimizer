"""
Testes de integração completa LLM com otimização de rotas

IMPORTANTE: Estes testes funcionam com QUALQUER provedor LLM configurado no .env:
- OpenAI (se LLM_PROVIDER=openai e OPENAI_API_KEY estiver configurada)
- Ollama (se LLM_PROVIDER=ollama e Ollama estiver rodando)

O provedor é detectado automaticamente pela função create_llm_provider().

Markers:
@pytest.fixture: Funções que configuram o ambiente de teste
@pytest.mark.integration: Testes de integração que precisam de conexão real com LLM
@pytest.mark.llm: Testes relacionados a provedores LLM
"""

import pytest
import os
from dotenv import load_dotenv

from src.core.service_points import create_service_point
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness
)
from src.llm import (
    create_llm_provider,
    get_available_providers,
    ManualGenerator,
    ItineraryGenerator,
    QAGenerator
)


# Carrega variáveis de ambiente
load_dotenv()


@pytest.fixture
def sample_points():
    """ Fixture que cria pontos de serviço de exemplo """
    points = [
        # Depósito
        create_service_point(0, (0, 0), 'regular'),
        
        # Emergências (prioridade máxima)
        create_service_point(1, (10, 15), 'emergency'),
        create_service_point(2, (25, 30), 'emergency'),
        
        # Violência doméstica
        create_service_point(3, (40, 20), 'violence', time_window=(480, 600)),
        
        # Medicamentos hormonais
        create_service_point(4, (15, 25), 'medication'),
        create_service_point(5, (35, 35), 'medication'),
        
        # Pós-parto
        create_service_point(6, (20, 10), 'postpartum', time_window=(540, 660)),
        
        # Regular
        create_service_point(7, (30, 15), 'regular'),
        create_service_point(8, (45, 25), 'regular'),
    ]
    
    return points


@pytest.fixture
def optimized_route(sample_points):
    """ Fixture que otimiza rota usando algoritmo genético """
    # Gera população inicial
    population = generate_priority_aware_population(sample_points, population_size=50)
    
    # Encontra melhor rota
    best_route = None
    best_fitness = float('inf')
    
    for route in population:
        fitness = calculate_constrained_fitness(route)
        if fitness < best_fitness:
            best_fitness = fitness
            best_route = route
    
    return best_route


@pytest.fixture
def llm_provider():
    """ Fixture que cria provedor LLM (OpenAI ou Ollama, conforme .env) """
    try:
        provider = create_llm_provider()
        return provider
    except Exception as e:
        pytest.skip(f"LLM provider não disponível: {e}")


class TestLLMProviders:
    """ Testes para provedores LLM disponíveis """
    
    def test_get_available_providers(self):
        """ Testa listagem de provedores disponíveis """
        providers = get_available_providers()
        
        # Verifica que retorna um dicionário
        assert isinstance(providers, dict)
        assert len(providers) > 0
        
        # Verifica estrutura de cada provedor
        for name, info in providers.items():
            assert 'name' in info
            assert 'requires_api_key' in info
            assert 'cost' in info
            assert 'privacy' in info
    
    def test_provider_info_structure(self):
        """ Testa estrutura das informações dos provedores """
        providers = get_available_providers()
        
        # Verifica que OpenAI está disponível
        assert 'openai' in providers
        openai_info = providers['openai']
        
        assert openai_info['name'] == 'OpenAI'
        assert openai_info['requires_api_key'] is True
        assert isinstance(openai_info['cost'], str)
        assert isinstance(openai_info['privacy'], str)
        
        # Verifica que Ollama está disponível
        assert 'ollama' in providers
        ollama_info = providers['ollama']
        
        assert 'Ollama' in ollama_info['name']
        assert ollama_info['requires_api_key'] is False
        assert isinstance(ollama_info['cost'], str)
        assert isinstance(ollama_info['privacy'], str)


class TestRouteOptimization:
    """ Testes para otimização de rotas """
    
    def test_create_sample_points(self, sample_points):
        """ Testa criação de pontos de exemplo """
        assert len(sample_points) == 9
        assert sample_points[0].id == 0  # Depósito
        assert sample_points[1].priority.name == 'EMERGENCY_OBSTETRIC'
        assert sample_points[3].priority.name == 'DOMESTIC_VIOLENCE'
    
    def test_optimize_route(self, optimized_route, sample_points):
        """ Testa otimização de rota """
        assert optimized_route is not None
        assert len(optimized_route) == len(sample_points)
        
        # Verifica que o depósito é o primeiro ponto
        assert optimized_route[0].id == 0
        
        # Verifica que todos os pontos estão na rota
        route_ids = {point.id for point in optimized_route}
        expected_ids = {point.id for point in sample_points}
        assert route_ids == expected_ids
    
    def test_route_fitness(self, optimized_route):
        """ Testa cálculo de fitness da rota """
        fitness = calculate_constrained_fitness(optimized_route)
        
        assert isinstance(fitness, (int, float))
        assert fitness >= 0


@pytest.mark.integration
class TestManualGenerator:
    """ Testes para gerador de manual de instruções """
    
    def test_generate_manual(self, llm_provider, optimized_route):
        """ Testa geração de manual de instruções """
        generator = ManualGenerator(llm_provider)
        
        manual = generator.generate_manual(
            route=optimized_route,
            start_time=480.0,
            speed=60.0
        )
        
        # Verifica que o manual foi gerado
        assert manual is not None
        assert isinstance(manual, str)
        assert len(manual) > 100  # Manual deve ter conteúdo substancial
        
        print(f"\n[DEBUG] Manual gerado ({len(manual)} caracteres)")
    
    def test_manual_content(self, llm_provider, optimized_route):
        """ Testa conteúdo do manual gerado """
        generator = ManualGenerator(llm_provider)
        
        manual = generator.generate_manual(
            route=optimized_route,
            start_time=480.0,
            speed=60.0
        )
        
        # Verifica palavras-chave esperadas no manual
        manual_lower = manual.lower()
        assert any(word in manual_lower for word in ['manual', 'instruções', 'rota'])


@pytest.mark.integration
class TestItineraryGenerator:
    """ Testes para gerador de roteiro detalhado """
    
    def test_generate_itinerary(self, llm_provider, optimized_route):
        """Testa geração de roteiro detalhado."""
        generator = ItineraryGenerator(llm_provider)
        arrival_times = [480 + i * 30 for i in range(len(optimized_route))]
        
        itinerary = generator.generate_detailed_itinerary(
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        
        # Verifica que o roteiro foi gerado
        assert itinerary is not None
        assert isinstance(itinerary, str)
        assert len(itinerary) > 100
        
        print(f"\n[DEBUG] Roteiro gerado ({len(itinerary)} caracteres)")
    
    def test_itinerary_content(self, llm_provider, optimized_route):
        """ Testa conteúdo do roteiro gerado """
        generator = ItineraryGenerator(llm_provider)
        arrival_times = [480 + i * 30 for i in range(len(optimized_route))]
        
        itinerary = generator.generate_detailed_itinerary(
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        
        # Verifica palavras-chave esperadas
        itinerary_lower = itinerary.lower()
        assert any(word in itinerary_lower for word in ['roteiro', 'parada', 'horário'])


@pytest.mark.integration
class TestQAGenerator:
    """ Testes para sistema de perguntas e respostas """
    
    def test_answer_question(self, llm_provider, optimized_route):
        """Testa resposta a pergunta sobre a rota."""
        generator = QAGenerator(llm_provider)
        arrival_times = [480 + i * 30 for i in range(len(optimized_route))]
        
        answer = generator.answer_question(
            question="Quantas paradas temos hoje?",
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        
        # Verifica que a resposta foi gerada
        assert answer is not None
        assert isinstance(answer, str)
        assert len(answer) > 10
        
        print(f"\n[DEBUG] Resposta: {answer}")
    
    @pytest.mark.parametrize("question", [
        "Qual o próximo atendimento prioritário?",
        "Quantas paradas de emergência temos?",
        "Há casos de violência doméstica na rota?",
        "Qual o tempo total estimado da rota?",
    ])
    def test_multiple_questions(self, llm_provider, optimized_route, question):
        """ Testa múltiplas perguntas sobre a rota """
        generator = QAGenerator(llm_provider)
        arrival_times = [480 + i * 30 for i in range(len(optimized_route))]
        
        answer = generator.answer_question(
            question=question,
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        
        # Verifica que cada pergunta recebe uma resposta
        assert answer is not None
        assert isinstance(answer, str)
        assert len(answer) > 0
        
        print(f"\n[DEBUG] Q: {question}")
        print(f"[DEBUG] A: {answer[:100]}...")


@pytest.mark.integration
class TestFullIntegration:
    """ Testes de integração completa do sistema """
    
    def test_complete_workflow(self, llm_provider, optimized_route):
        """ Testa fluxo completo: otimização + geração de conteúdo """
        arrival_times = [480 + i * 30 for i in range(len(optimized_route))]
        
        # 1. Gera manual
        manual_gen = ManualGenerator(llm_provider)
        manual = manual_gen.generate_manual(
            route=optimized_route,
            start_time=480.0,
            speed=60.0
        )
        assert manual is not None
        
        # 2. Gera roteiro
        itinerary_gen = ItineraryGenerator(llm_provider)
        itinerary = itinerary_gen.generate_detailed_itinerary(
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        assert itinerary is not None
        
        # 3. Responde perguntas
        qa_gen = QAGenerator(llm_provider)
        answer = qa_gen.answer_question(
            question="Qual a primeira parada?",
            route=optimized_route,
            arrival_times=arrival_times,
            total_distance=100.5,
            total_time=480
        )
        assert answer is not None
        
        print("\n[DEBUG] Fluxo completo executado com sucesso!")
        print(f"  - Manual: {len(manual)} caracteres")
        print(f"  - Roteiro: {len(itinerary)} caracteres")
        print(f"  - Resposta Q&A: {len(answer)} caracteres")


# Testes que não requerem integração
class TestBasicFunctionality:
    """ Testes básicos que não requerem LLM """
    
    def test_service_point_creation(self):
        """ Testa criação de pontos de serviço """
        point = create_service_point(1, (10, 20), 'emergency')
        
        assert point.id == 1
        assert point.location == (10, 20)
        assert point.priority.name == 'EMERGENCY_OBSTETRIC'
        assert point.requires_special_protocol is True
    
    def test_population_generation(self, sample_points):
        """ Testa geração de população inicial """
        population = generate_priority_aware_population(sample_points, population_size=10)
        
        assert len(population) == 10
        assert all(len(route) == len(sample_points) for route in population)
