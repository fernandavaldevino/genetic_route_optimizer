"""
API FastAPI para Sistema de Otimização de Rotas
Fornece endpoints REST para otimização de rotas e gerenciamento de dados
"""

import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Carregar variáveis de ambiente
load_dotenv(ROOT_DIR / '.env')

from api.models import (
    OptimizationRequest,
    OptimizationResponse,
    RouteListResponse,
    HealthResponse,
    ErrorResponse
)
from src.core.service_points import create_service_point, calculate_distance
from src.core.genetic_algorithm import (
    generate_priority_aware_population,
    calculate_constrained_fitness,
    constrained_order_crossover,
    constrained_mutate,
    sort_population_by_fitness
)
from telegram_bot.route_integration import RouteDataIntegration

# Criar aplicação FastAPI
app = FastAPI(
    title="Sistema de Otimização de Rotas",
    description="API REST para otimização de rotas de atendimento com algoritmo genético",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instância de integração de rotas
route_integration = RouteDataIntegration()

# Instância do bot do Telegram inicializada sob demanda
telegram_bot = None


def get_telegram_bot():
    """ Obtém ou cria a instância do bot do Telegram """
    global telegram_bot
    if telegram_bot is None:
        try:
            from telegram import Bot
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if token:
                telegram_bot = Bot(token=token)
                print("✅ Bot do Telegram inicializado para webhook")
            else:
                print("⚠️ TELEGRAM_BOT_TOKEN não configurado")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar bot: {e}")
    return telegram_bot


@app.get("/", tags=["Root"])
async def root():
    """ Endpoint raiz da API """
    return {
        "message": "API de Otimização de Rotas",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "webhook": "/webhook"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """ Verifica o status da API """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.post(
    "/api/v1/optimize",
    response_model=OptimizationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Optimization"],
    summary="Otimizar rota",
    description="Executa o algoritmo genético para otimizar a rota de atendimento"
)
async def optimize_route(request: OptimizationRequest):
    """ Otimiza a rota de atendimento usando algoritmo genético """
    try:
        start_time = time.time()
        
        # Criar depósito
        depot_loc = request.depot_location or (250.0, 250.0)
        depot = create_service_point(0, depot_loc, 'regular', None)
        depot.service_duration = 0.0
        
        # Criar pontos de serviço
        service_points = [depot]
        for point_input in request.service_points:
            point = create_service_point(
                id=point_input.id,
                location=point_input.location,
                service_type=point_input.service_type.value,
                time_window=point_input.time_window
            )
            service_points.append(point)
        
        # Executar algoritmo genético
        # Gerar população inicial
        population = generate_priority_aware_population(
            service_points,
            request.population_size
        )
        
        # Evoluir população
        for generation in range(request.generations):
            # Calcular fitness
            fitness_values = [
                calculate_constrained_fitness(route, speed=60.0, priority_deadline=1440.0)
                for route in population
            ]
            
            # Ordenar por fitness
            population, fitness_values = sort_population_by_fitness(population, fitness_values)
            
            # Elitismo: manter os 20% melhores
            elite_size = max(1, request.population_size // 5)
            new_population = population[:elite_size]
            
            # Gerar nova população
            while len(new_population) < request.population_size:
                # Seleção por torneio
                tournament_size = 3
                tournament = random.sample(list(zip(population, fitness_values)), tournament_size)
                parent1 = min(tournament, key=lambda x: x[1])[0]
                
                tournament = random.sample(list(zip(population, fitness_values)), tournament_size)
                parent2 = min(tournament, key=lambda x: x[1])[0]
                
                # Crossover
                child = constrained_order_crossover(parent1, parent2)
                
                # Mutação
                child = constrained_mutate(child, mutation_probability=0.1)
                
                new_population.append(child)
            
            population = new_population
        
        # Obter melhor solução
        fitness_values = [
            calculate_constrained_fitness(route, speed=60.0, priority_deadline=1440.0)
            for route in population
        ]
        best_idx = fitness_values.index(min(fitness_values))
        best_route = population[best_idx]
        best_fitness = fitness_values[best_idx]
        
        # Calcular distância total
        total_distance = 0.0
        for i in range(len(best_route) - 1):
            p1 = best_route[i]
            p2 = best_route[i + 1]
            total_distance += calculate_distance(p1.location, p2.location) * 0.1  # Converter para km
        
        # Converter rota de objetos para índices
        best_route_indices = [point.id for point in best_route[1:]]  # Remover depósito
        
        # Converter para formato do bot
        route_data = route_integration.convert_from_optimization_result(
            best_route=best_route_indices,
            service_points=service_points,
            fitness=best_fitness,
            distance_km=total_distance,
            num_vehicles=request.num_vehicles
        )
        
        # Salvar rota
        route_integration.save_route(route_data)
        
        execution_time = time.time() - start_time
        
        # Preparar resposta
        return OptimizationResponse(
            success=True,
            message="Otimização concluída com sucesso",
            date=route_data['date'],
            fitness=route_data['fitness'],
            num_vehicles=route_data['num_vehicles'],
            vehicles=route_data['vehicles'],
            execution_time=round(execution_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro na otimização: {str(e)}"
        )


@app.get(
    "/api/v1/routes",
    response_model=RouteListResponse,
    tags=["Routes"],
    summary="Listar rotas salvas",
    description="Retorna lista de todas as rotas otimizadas salvas"
)
async def list_routes():
    """ Lista todas as rotas salvas """
    try:
        route_files = sorted(route_integration.data_dir.glob('route_*.json'), reverse=True)
        
        routes = []
        for route_file in route_files:
            import json
            with open(route_file, 'r', encoding='utf-8') as f:
                route_data = json.load(f)
                routes.append({
                    'filename': route_file.name,
                    'date': route_data.get('date'),
                    'num_vehicles': route_data.get('num_vehicles'),
                    'fitness': route_data.get('fitness')
                })
        
        return RouteListResponse(
            routes=routes,
            total=len(routes)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar rotas: {str(e)}"
        )


@app.get(
    "/api/v1/routes/latest",
    tags=["Routes"],
    summary="Obter rota mais recente",
    description="Retorna a rota otimizada mais recente"
)
async def get_latest_route():
    """ Retorna a rota mais recente """
    try:
        route_data = route_integration.load_latest_route()
        
        if not route_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma rota encontrada"
            )
        
        return route_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar rota: {str(e)}"
        )


@app.get(
    "/api/v1/routes/{filename}",
    tags=["Routes"],
    summary="Obter rota específica",
    description="Retorna uma rota específica pelo nome do arquivo"
)
async def get_route(filename: str):
    """ Retorna uma rota específica """
    try:
        import json
        route_file = route_integration.data_dir / filename
        
        if not route_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rota '{filename}' não encontrada"
            )
        
        with open(route_file, 'r', encoding='utf-8') as f:
            route_data = json.load(f)
        
        return route_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao carregar rota: {str(e)}"
        )


@app.get(
    "/api/v1/routes/summary",
    tags=["Routes"],
    summary="Resumo da rota atual",
    description="Retorna resumo da rota mais recente"
)
async def get_route_summary():
    """ Retorna resumo da rota atual """
    try:
        summary = route_integration.get_route_summary()
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhuma rota encontrada"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter resumo: {str(e)}"
        )


@app.get(
    "/api/v1/vehicles/{vehicle_id}",
    tags=["Vehicles"],
    summary="Obter dados de veículo",
    description="Retorna dados de um veículo específico"
)
async def get_vehicle_data(vehicle_id: int):
    """ Retorna dados de um veículo específico """
    try:
        vehicle_data = route_integration.get_vehicle_data(vehicle_id)
        
        if not vehicle_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Veículo {vehicle_id} não encontrado"
            )
        
        return vehicle_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter dados do veículo: {str(e)}"
        )


@app.post(
    "/webhook",
    tags=["Telegram"],
    summary="Webhook do Telegram",
    description="Recebe atualizações do Telegram via webhook"
)
async def telegram_webhook(request: Request):
    """ Endpoint de webhook do Telegram chamado sempre que há uma nova mensagem """
    try:
        # Obter dados do webhook
        update_data = await request.json()
        
        # Processar usando o webhook handler otimizado
        from telegram_bot.webhook_handler import process_telegram_update
        
        await process_telegram_update(update_data)
        
        # Sempre retornar 200 OK para o Telegram
        return {"ok": True}
        
    except Exception as e:
        print(f"❌ Erro no webhook: {e}")
        import traceback
        traceback.print_exc()
        # Retornar 200 mesmo com erro para evitar reenvios do Telegram
        return {"ok": True, "error": str(e)}


@app.get(
    "/webhook/info",
    tags=["Telegram"],
    summary="Informações do webhook",
    description="Retorna informações sobre a configuração do webhook"
)
async def webhook_info():
    """ Retorna informações sobre o webhook do Telegram para verificar se está configurado corretamente.
    """
    try:
        bot = get_telegram_bot()
        if not bot:
            return {
                "configured": False,
                "message": "Bot do Telegram não configurado. Configure TELEGRAM_BOT_TOKEN no .env"
            }
        
        # Obter informações do webhook
        webhook_info = await bot.get_webhook_info()
        
        return {
            "configured": True,
            "url": webhook_info.url,
            "has_custom_certificate": webhook_info.has_custom_certificate,
            "pending_update_count": webhook_info.pending_update_count,
            "last_error_date": webhook_info.last_error_date,
            "last_error_message": webhook_info.last_error_message,
            "max_connections": webhook_info.max_connections
        }
        
    except Exception as e:
        return {
            "configured": False,
            "error": str(e)
        }


# Tratamento de erros global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """ Tratador global de exceções """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
