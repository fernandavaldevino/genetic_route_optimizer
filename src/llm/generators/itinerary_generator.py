""" Gerador de Roteiro Detalhado de Visitas """

from typing import Dict, Any, List
from src.llm.providers.base import BaseLLMProvider
from src.llm.prompts.route_prompts import build_detailed_itinerary_prompt
from src.core.service_points import ServicePoint, calculate_distance


class ItineraryGenerator:
    """ Gerador de roteiros detalhados para motoristas """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """ Inicializa o gerador com um provedor LLM """
        self.llm_provider = llm_provider
    
    def generate_detailed_itinerary(
        self,
        route: List[ServicePoint],
        arrival_times: List[float],
        total_distance: float,
        total_time: float,
        speed: float = 60.0
    ) -> str:
        """ Gera roteiro detalhado de visitas para o motorista """
        route_data = {
            'route': route,
            'arrival_times': arrival_times,
            'total_distance': total_distance,
            'total_time': total_time,
            'speed': speed
        }
        
        prompt = build_detailed_itinerary_prompt(route_data)
        
        try:
            itinerary = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=4000,
                system_message="Você é um assistente de logística criando roteiros claros e fáceis de seguir."
            )
            return itinerary
        except Exception as e:
            return f"Erro ao gerar roteiro: {str(e)}"
    
    def generate_stop_details(
        self,
        point: ServicePoint,
        arrival_time: float,
        stop_number: int,
        previous_point: ServicePoint = None
    ) -> str:
        """ Gera detalhes específicos de uma parada """
        hours = int(arrival_time // 60)
        minutes = int(arrival_time % 60)
        
        # Calcular distância e tempo do ponto anterior
        distance_info = ""
        if previous_point:
            distance = calculate_distance(previous_point.location, point.location) * 0.1
            distance_info = f"\n- Distância do ponto anterior: {distance:.1f} km"
        
        # Informações da janela de tempo
        time_window_info = ""
        if point.time_window:
            tw_start_h = int(point.time_window.start_time // 60)
            tw_start_m = int(point.time_window.start_time % 60)
            tw_end_h = int(point.time_window.end_time // 60)
            tw_end_m = int(point.time_window.end_time % 60)
            time_window_info = f"\n- Janela de atendimento: {tw_start_h:02d}:{tw_start_m:02d} - {tw_end_h:02d}:{tw_end_m:02d}"
        
        prompt = f"""
Crie uma descrição detalhada para a seguinte parada:

Parada #{stop_number}
- Ponto ID: {point.id}
- Tipo de atendimento: {point.priority.name}
- Chegada prevista: {hours:02d}:{minutes:02d}
- Duração do atendimento: {point.service_duration} minutos{distance_info}{time_window_info}

Forneça:
1. Breve descrição do que fazer nesta parada
2. Cuidados específicos necessários
3. O que verificar antes de sair

Seja conciso (máximo 150 palavras).
"""
        
        try:
            details = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=300,
                system_message="Você é um assistente criando instruções práticas para motoristas."
            )
            return details
        except Exception as e:
            return f"Erro ao gerar detalhes da parada: {str(e)}"
    
    def generate_time_summary(
        self,
        route: List[ServicePoint],
        arrival_times: List[float]
    ) -> str:
        """ Gera resumo de horários críticos da rota """
        # Identificar horários críticos
        critical_times = []
        
        for i, point in enumerate(route):
            if point.id == 0:
                continue
                
            arrival = arrival_times[i] if i < len(arrival_times) else 0
            
            # Emergências
            if point.priority.value == 1:
                critical_times.append(f"URGENTE - Ponto {point.id}: chegada às {int(arrival//60):02d}:{int(arrival%60):02d}")
            
            # Janelas de tempo
            elif point.time_window:
                tw_end = point.time_window.end_time
                critical_times.append(f"Janela de tempo - Ponto {point.id}: atender até {int(tw_end//60):02d}:{int(tw_end%60):02d}")
        
        critical_text = "\n".join(critical_times) if critical_times else "Nenhum horário crítico identificado"
        
        prompt = f"""
Com base nos seguintes horários críticos da rota:

{critical_text}

Crie um RESUMO DE HORÁRIOS destacando:
1. Horários que não podem ser perdidos
2. Margem de flexibilidade (se houver)
3. Recomendações de gestão de tempo
4. O que fazer em caso de atraso

Seja prático e direto. Máximo 200 palavras.
"""
        
        try:
            summary = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=400,
                system_message="Você é um especialista em gestão de tempo para operações logísticas."
            )
            return summary
        except Exception as e:
            return f"Erro ao gerar resumo de horários: {str(e)}"
    
    def generate_navigation_tips(
        self,
        route: List[ServicePoint]
    ) -> str:
        """ Gera dicas de navegação e otimização de tempo """
        num_stops = len([p for p in route if p.id != 0])
        has_time_windows = any(p.time_window for p in route if p.id != 0)
        has_priorities = any(p.priority.value <= 2 for p in route if p.id != 0)
        
        prompt = f"""
Para uma rota com {num_stops} paradas, onde:
- Há janelas de tempo restritas: {'SIM' if has_time_windows else 'NÃO'}
- Há atendimentos prioritários: {'SIM' if has_priorities else 'NÃO'}

Forneça DICAS DE NAVEGAÇÃO E GESTÃO DE TEMPO:
1. Como se preparar antes de sair
2. O que fazer se houver trânsito inesperado
3. Como gerenciar pausas e descansos
4. Dicas para manter o cronograma
5. Quando comunicar atrasos à central

Seja prático e focado em ações concretas. Máximo 250 palavras.
"""
        
        try:
            tips = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=500,
                system_message="Você é um motorista experiente compartilhando dicas práticas."
            )
            return tips
        except Exception as e:
            return f"Erro ao gerar dicas de navegação: {str(e)}"
    
    def generate_multi_vehicle_itinerary(
        self,
        vehicles_data: List[Dict[str, Any]]
    ) -> Dict[int, str]:
        """ Gera roteiros individuais para cada veículo em operação multi-veículo """
        itineraries = {}
        
        for vehicle_data in vehicles_data:
            vehicle_id = vehicle_data.get('vehicle_id', 0)
            route = vehicle_data.get('route', [])
            arrival_times = vehicle_data.get('arrival_times', [])
            total_distance = vehicle_data.get('total_distance', 0)
            total_time = vehicle_data.get('total_time', 0)
            
            itinerary = self.generate_detailed_itinerary(
                route=route,
                arrival_times=arrival_times,
                total_distance=total_distance,
                total_time=total_time
            )
            
            itineraries[vehicle_id] = itinerary
        
        return itineraries
