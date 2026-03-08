"""
Exemplo completo de integração LLM com otimização de rotas
"""

import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.service_points import create_service_point
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness
)
from src.llm import (
    create_llm_provider,
    get_available_providers,
    ManualGenerator,
    RouteGenerator,
    QASystem
)


def create_sample_route():
    """Cria rota de exemplo."""
    print("📍 Criando rota de exemplo...")
    
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


def optimize_route(points):
    """Otimiza rota usando algoritmo genético."""
    print("\n🧬 Otimizando rota com algoritmo genético...")
    
    # Gera população inicial
    population = generate_priority_aware_population(points, population_size=50)
    
    # Encontra melhor rota (simplificado - apenas da população inicial)
    best_route = None
    best_fitness = float('inf')
    
    for route in population:
        fitness = calculate_constrained_fitness(route)
        if fitness < best_fitness:
            best_fitness = fitness
            best_route = route
    
    print(f"✅ Rota otimizada! Fitness: {best_fitness:.2f}")
    return best_route


def main():
    """Função principal do exemplo."""
    print("=" * 60)
    print("🚀 EXEMPLO: INTEGRAÇÃO LLM COM OTIMIZAÇÃO DE ROTAS")
    print("=" * 60)
    
    # 1. Lista provedores disponíveis
    print("\n📋 Provedores de LLM disponíveis:")
    providers = get_available_providers()
    for name, info in providers.items():
        print(f"\n  {name.upper()}:")
        print(f"    - Nome: {info['name']}")
        print(f"    - Requer API key: {info['requires_api_key']}")
        print(f"    - Custo: {info['cost']}")
        print(f"    - Privacidade: {info['privacy']}")
    
    # 2. Cria rota de exemplo
    points = create_sample_route()
    print(f"\n✅ {len(points)} pontos criados")
    
    # 3. Otimiza rota
    optimized_route = optimize_route(points)
    
    # 4. Cria provedor LLM
    print("\n🤖 Inicializando provedor LLM...")
    try:
        provider = create_llm_provider()
        print(f"✅ Provedor inicializado: {provider.model}")
    except Exception as e:
        print(f"❌ Erro ao criar provedor: {e}")
        print("\n💡 Dica: Configure o arquivo .env com suas credenciais")
        return
    
    # 5. Gera manual de instruções
    print("\n" + "=" * 60)
    print("📖 GERANDO MANUAL DE INSTRUÇÕES")
    print("=" * 60)
    
    try:
        manual_gen = ManualGenerator(provider)
        manual = manual_gen.generate_manual(optimized_route)
        
        print("\n" + manual)
        
        # Salva manual
        manual_gen.save_manual(manual, "manual_rota_exemplo.txt")
        
    except Exception as e:
        print(f"❌ Erro ao gerar manual: {e}")
    
    # 6. Gera roteiro detalhado
    print("\n" + "=" * 60)
    print("🗺️  GERANDO ROTEIRO DETALHADO")
    print("=" * 60)
    
    try:
        route_gen = RouteGenerator(provider)
        roteiro = route_gen.generate_route_description(optimized_route)
        
        print("\n" + roteiro)
        
        # Salva roteiro
        route_gen.save_route(roteiro, "roteiro_rota_exemplo.txt")
        
    except Exception as e:
        print(f"❌ Erro ao gerar roteiro: {e}")
    
    # 7. Sistema de perguntas e respostas
    print("\n" + "=" * 60)
    print("❓ SISTEMA DE PERGUNTAS E RESPOSTAS")
    print("=" * 60)
    
    try:
        qa = QASystem(provider)
        qa.set_route(optimized_route)
        
        # Perguntas de exemplo
        perguntas = [
            "Qual o próximo atendimento prioritário?",
            "Quantas paradas de emergência temos hoje?",
            "Há casos de violência doméstica na rota?",
            "Qual o tempo total estimado da rota?"
        ]
        
        for pergunta in perguntas:
            print(f"\n❓ {pergunta}")
            resposta = qa.ask(pergunta)
            print(f"💬 {resposta}")
        
        # Mostra histórico
        print("\n📜 Histórico de conversação:")
        history = qa.get_conversation_history()
        print(f"   Total de perguntas: {len(history)}")
        
    except Exception as e:
        print(f"❌ Erro no sistema Q&A: {e}")
    
    print("\n" + "=" * 60)
    print("✅ EXEMPLO CONCLUÍDO!")
    print("=" * 60)
    print("\n📁 Arquivos gerados:")
    print("   - manual_rota_exemplo.txt")
    print("   - roteiro_rota_exemplo.txt")


if __name__ == "__main__":
    main()
