""" Utilitários para integração LLM com Streamlit """

from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from src.llm.providers.openai_provider import OpenAIProvider
from src.llm.providers.base import BaseLLMProvider
from src.llm.generators.manual_generator import ManualGenerator
from src.llm.generators.itinerary_generator import ItineraryGenerator
from src.llm.generators.qa_generator import QAGenerator
from src.core.service_points import ServicePoint
from src.core.genetic_algorithm import calculate_route_time_and_distance

import os


def load_llm_provider() -> Optional[BaseLLMProvider]:
    """ Carrega o provedor LLM configurado no arquivo .env """
    load_dotenv()
    
    provider_type = os.getenv('LLM_PROVIDER', 'openai').lower()
    
    if provider_type == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo').strip('"')
        temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        
        if not api_key:
            return None
        
        try:
            provider = OpenAIProvider(
                api_key=api_key,
                model=model,
                temperature=temperature
            )
            return provider
        except Exception as e:
            print(f"Erro ao carregar provedor OpenAI: {e}")
            return None
    
    # Adicionar suporte para outros provedores aqui (Ollama, etc.)
    
    return None


def validate_llm_connection(provider: BaseLLMProvider) -> bool:
    """ Valida a conexão com o provedor LLM """
    try:
        return provider.validate_connection()
    except Exception as e:
        print(f"Erro ao validar conexão: {e}")
        return False


def prepare_route_data_single_vehicle(route: List[ServicePoint],
                                      arrival_times: List[float],
                                      best_fitness: float) -> Dict[str, Any]:
    """ Prepara dados da rota para um único veículo """
    
    total_distance, total_time, _ = calculate_route_time_and_distance(route)
    total_distance_km = total_distance * 0.1
    
    return {
        'route': route,
        'arrival_times': arrival_times,
        'total_distance': total_distance_km,
        'total_time': total_time,
        'fitness': best_fitness,
        'num_vehicles': 1
    }


def prepare_route_data_multi_vehicle(
    best_solution: Any
) -> List[Dict[str, Any]]:
    """ Prepara dados da rota para múltiplos veículos """
    vehicles_data = []
    
    for vehicle in best_solution.vehicles:
        # Calcular tempos de chegada para este veículo
        from src.core.genetic_algorithm import calculate_route_time_and_distance
        _, _, arrival_times = calculate_route_time_and_distance(vehicle.route)
        
        vehicle_data = {
            'vehicle_id': vehicle.vehicle_id,
            'route': vehicle.route,
            'arrival_times': arrival_times,
            'total_distance': vehicle.total_distance * 0.1,  # Converter para km
            'total_time': vehicle.total_time
        }
        vehicles_data.append(vehicle_data)
    
    return vehicles_data


class LLMIntegration:
    """ Classe principal para integração LLM com Streamlit """
    
    def __init__(self):
        """ Inicializa a integração LLM """
        self.provider = None
        self.manual_generator = None
        self.itinerary_generator = None
        self.qa_generator = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """ Inicializa os geradores LLM e valida a conexão """
        self.provider = load_llm_provider()
        
        if not self.provider:
            return False
        
        if not validate_llm_connection(self.provider):
            return False
        
        self.manual_generator = ManualGenerator(self.provider)
        self.itinerary_generator = ItineraryGenerator(self.provider)
        self.qa_generator = QAGenerator(self.provider)
        self.is_initialized = True
        
        return True
    
    def generate_manual(self,
                        route: List[ServicePoint],
                        arrival_times: List[float],
                        total_distance: float,
                        total_time: float,
                        is_multi_vehicle: bool = False,
                        vehicles_data: Optional[List[Dict[str, Any]]] = None) -> str:
        """ Gera manual de instruções """
        if not self.is_initialized:
            return "LLM não inicializado. Verifique as configurações."
        
        try:
            if is_multi_vehicle and vehicles_data:
                return self.manual_generator.generate_multi_vehicle_manual(vehicles_data)
            else:
                return self.manual_generator.generate_single_vehicle_manual(
                    route, arrival_times, total_distance, total_time
                )
        except Exception as e:
            return f" Erro ao gerar manual: {str(e)}"
    
    def generate_itinerary(
        self,
        route: List[ServicePoint],
        arrival_times: List[float],
        total_distance: float,
        total_time: float
    ) -> str:
        """ Gera roteiro detalhado """
        if not self.is_initialized:
            return "LLM não inicializado. Verifique as configurações."
        
        try:
            return self.itinerary_generator.generate_detailed_itinerary(
                route, arrival_times, total_distance, total_time
            )
        except Exception as e:
            return f"Erro ao gerar roteiro: {str(e)}"
    
    def answer_question(
        self,
        question: str,
        route: List[ServicePoint],
        arrival_times: List[float],
        total_distance: float,
        total_time: float
    ) -> str:
        """ Responde pergunta sobre a rota """
        if not self.is_initialized:
            return "LLM não inicializado. Verifique as configurações."
        
        try:
            return self.qa_generator.answer_question(
                question, route, arrival_times, total_distance, total_time
            )
        except Exception as e:
            return f"Erro ao responder pergunta: {str(e)}"
    
    def get_suggested_questions(self,
                                route: List[ServicePoint]) -> List[str]:
        """ Obtém sugestões de perguntas """
        if not self.is_initialized:
            return []
        
        try:
            return self.qa_generator.get_suggested_questions(route)
        except Exception as e:
            return []
    
    def generate_priority_summary(self,
                                  route: List[ServicePoint],
                                  include_emojis: bool = True) -> str:
        """ Gera resumo de prioridades """
        if not self.is_initialized:
            return "LLM não inicializado. Verifique as configurações."
        
        try:
            return self.manual_generator.generate_priority_summary(route, include_emojis)
        except Exception as e:
            return f"Erro ao gerar resumo: {str(e)}"
    
    def generate_checklist(self,
                           route: List[ServicePoint]) -> str:
        """ Gera checklist pré-operação """
        if not self.is_initialized:
            return "LLM não inicializado. Verifique as configurações."
        
        try:
            return self.manual_generator.generate_checklist(route)
        except Exception as e:
            return f"Erro ao gerar checklist: {str(e)}"
    
    def generate_multi_vehicle_itineraries_zip(self, vehicles_data: List[Dict[str, Any]]) -> bytes:
        """ Gera múltiplos PDFs de roteiros (um por veículo) e retorna como arquivo ZIP """
        if not self.is_initialized:
            raise RuntimeError("LLM não inicializado. Verifique as configurações.")
        
        from src.llm.utils.pdf_generator import generate_multi_vehicle_itineraries_zip
        return generate_multi_vehicle_itineraries_zip(vehicles_data, self)
    
    def generate_multi_vehicle_priorities_zip(self, vehicles_data: List[Dict[str, Any]]) -> bytes:
        """ Gera múltiplos PDFs de resumo de prioridades (um por veículo) e retorna como arquivo ZIP """
        if not self.is_initialized:
            raise RuntimeError("LLM não inicializado. Verifique as configurações.")
        
        from src.llm.utils.pdf_generator import generate_multi_vehicle_priorities_zip
        return generate_multi_vehicle_priorities_zip(vehicles_data, self)
    
    def clear_conversation_history(self):
        """ Limpa histórico de conversação do Q&A generator """
        if self.is_initialized and self.qa_generator:
            self.qa_generator.clear_history()
