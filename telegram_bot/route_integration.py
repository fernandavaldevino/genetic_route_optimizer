"""
Módulo de integração entre o Bot de Telegram e o Sistema de Otimização de Rotas
Carrega dados reais das rotas otimizadas para fornecer ao bot
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RouteDataIntegration:
    """ Integra dados do sistema de otimização com o bot """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """ Inicializa a integração """
        if data_dir is None:
            # Usa diretório padrão no projeto
            self.data_dir = Path(__file__).parent.parent / 'data' / 'routes'
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.current_route = None
    
    def load_latest_route(self) -> Optional[Dict]:
        """ Carrega a rota mais recente salva """
        try:
            # Procura por arquivos JSON de rotas
            route_files = sorted(self.data_dir.glob('route_*.json'), reverse=True)
            
            if route_files:
                with open(route_files[0], 'r', encoding='utf-8') as f:
                    self.current_route = json.load(f)
                    return self.current_route
            
            return None
        except Exception as e:
            print(f"Erro ao carregar rota: {e}")
            return None
    
    def save_route(self, route_data: Dict, filename: Optional[str] = None) -> bool:
        """ Salva dados de uma rota """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'route_{timestamp}.json'
            
            filepath = self.data_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(route_data, f, indent=2, ensure_ascii=False)
            
            self.current_route = route_data
            return True
        except Exception as e:
            print(f"Erro ao salvar rota: {e}")
            return False
    
    def get_route_summary(self) -> Optional[Dict]:
        """ Retorna resumo da rota atual """
        if not self.current_route:
            self.load_latest_route()
        
        if not self.current_route:
            return None
        
        return {
            'total_vehicles': len(self.current_route.get('vehicles', [])),
            'total_stops': sum(
                v.get('total_stops', 0) 
                for v in self.current_route.get('vehicles', [])
            ),
            'total_distance': sum(
                v.get('total_distance', 0) 
                for v in self.current_route.get('vehicles', [])
            ),
            'optimization_date': self.current_route.get('date', 'N/A')
        }
    
    def get_vehicle_data(self, vehicle_id: int = 1) -> Optional[Dict]:
        """ Retorna dados de um veículo específico """
        if not self.current_route:
            self.load_latest_route()
        
        if not self.current_route:
            return None
        
        vehicles = self.current_route.get('vehicles', [])
        
        for vehicle in vehicles:
            if vehicle.get('id') == vehicle_id:
                return vehicle
        
        return None
    
    def convert_from_optimization_result(self,
                                         best_route: List[int],
                                         service_points: List,
                                         fitness: float,
                                         distance_km: float,
                                         num_vehicles: int = 1) -> Dict:
        """ Converte resultado da otimização para formato do bot """
        route_data = {
            'date': datetime.now().isoformat(),
            'fitness': fitness,
            'num_vehicles': num_vehicles,
            'vehicles': []
        }
        
        if num_vehicles == 1:
            # Rota com 1 veículo
            stops = []
            current_time = 8 * 60       # 8:00 AM em minutos
            start_time = current_time   # Guardar horário de início
            first_stop_time = None
            last_stop_end_time = None
            
            for idx, point_idx in enumerate(best_route, 1):
                point = service_points[point_idx]
                
                # Guardar horário da primeira parada
                if first_stop_time is None:
                    first_stop_time = current_time
                
                service_type = self._get_service_type_from_priority(point)
                stop = {
                    'id': idx,
                    'type': service_type,
                    'priority': point.priority.value,
                    'address': f"Ponto {point_idx} - {service_type}",
                    'coordinates': {'x': point.location[0], 'y': point.location[1]},
                    'time': f"{int(current_time // 60):02d}:{int(current_time % 60):02d}",
                    'duration': f"{int(point.service_duration)} min",
                    'instructions': self._get_instructions(service_type),
                    'special_notes': self._get_special_notes(point)
                }
                
                stops.append(stop)
                
                # Atualizar tempo (adicionar duração da parada + tempo de viagem)
                current_time += point.service_duration + 10
                last_stop_end_time = current_time
            
            # Calcular tempo total de trabalho e agrupar paradas por dia
            days = []
            current_day_stops = []
            previous_time_mins = None
            
            for stop in stops:
                time_str = stop['time']
                hours, mins = map(int, time_str.split(':'))
                stop_time_mins = hours * 60 + mins
                
                # Detectar mudança de dia (horário volta para trás)
                if previous_time_mins is not None and stop_time_mins < previous_time_mins:
                    if current_day_stops:
                        days.append(current_day_stops)
                    current_day_stops = [stop]
                else:
                    current_day_stops.append(stop)
                
                duration_mins = int(stop['duration'].split()[0])
                previous_time_mins = stop_time_mins + duration_mins
            
            # Adicionar último dia
            if current_day_stops:
                days.append(current_day_stops)
            
            # Calcular tempo de trabalho de cada dia (SEM contar descanso)
            total_time_minutes = 0
            for day_stops in days:
                # Tempo do dia = (horário fim última parada) - (horário início primeira parada)
                first_time = day_stops[0]['time']
                first_h, first_m = map(int, first_time.split(':'))
                first_mins = first_h * 60 + first_m
                
                last_time = day_stops[-1]['time']
                last_h, last_m = map(int, last_time.split(':'))
                last_mins = last_h * 60 + last_m
                last_duration = int(day_stops[-1]['duration'].split()[0])
                
                # Tempo de trabalho do dia (início até fim + duração da última parada)
                day_time = (last_mins + last_duration) - first_mins
                total_time_minutes += day_time
            
            vehicle_data = {
                'id': 1,
                'driver': 'Motorista 1',
                'total_stops': len(stops),
                'total_distance': round(distance_km, 2),
                'estimated_time': f"{total_time_minutes // 60}h {total_time_minutes % 60}min",
                'start_time': '08:00',
                'end_time': f"{int(current_time // 60):02d}:{int(current_time % 60):02d}",
                'stops': stops
            }
            
            route_data['vehicles'].append(vehicle_data)
        
        else:
            # Rota com 2 veículos (implementação simplificada)
            # Divide pontos entre os veículos
            mid_point = len(best_route) // 2
            
            for vehicle_id in [1, 2]:
                if vehicle_id == 1:
                    vehicle_route = best_route[:mid_point]
                else:
                    vehicle_route = best_route[mid_point:]
                
                stops = []
                current_time = 8 * 60
                
                for idx, point_idx in enumerate(vehicle_route, 1):
                    point = service_points[point_idx]
                    service_type = self._get_service_type_from_priority(point)
                    
                    stop = {
                        'id': idx,
                        'type': service_type,
                        'priority': point.priority.value,
                        'address': f"Ponto {point_idx} - {service_type}",
                        'coordinates': {'x': point.location[0], 'y': point.location[1]},
                        'time': f"{int(current_time // 60):02d}:{int(current_time % 60):02d}",
                        'duration': f"{int(point.service_duration)} min",
                        'instructions': self._get_instructions(service_type),
                        'special_notes': self._get_special_notes(point)
                    }
                    
                    stops.append(stop)
                    current_time += point.service_duration + 10
                
                # Calcular tempo total considerando múltiplos dias e agrupar paradas por dia
                days = []
                current_day_stops = []
                previous_time_mins = None
                
                for stop in stops:
                    time_str = stop['time']
                    hours, mins = map(int, time_str.split(':'))
                    stop_time_mins = hours * 60 + mins
                    
                    # Detectar mudança de dia
                    if previous_time_mins is not None and stop_time_mins < previous_time_mins:
                        if current_day_stops:
                            days.append(current_day_stops)
                        current_day_stops = [stop]
                    else:
                        current_day_stops.append(stop)
                    
                    duration_mins = int(stop['duration'].split()[0])
                    previous_time_mins = stop_time_mins + duration_mins
                
                # Adicionar último dia
                if current_day_stops:
                    days.append(current_day_stops)
                
                # Calcular tempo de cada dia
                total_time_minutes = 0
                for day_stops in days:
                    first_time = day_stops[0]['time']
                    first_h, first_m = map(int, first_time.split(':'))
                    first_mins = first_h * 60 + first_m
                    
                    last_time = day_stops[-1]['time']
                    last_h, last_m = map(int, last_time.split(':'))
                    last_mins = last_h * 60 + last_m
                    last_duration = int(day_stops[-1]['duration'].split()[0])
                    
                    day_time = (last_mins + last_duration) - first_mins
                    total_time_minutes += day_time
                
                vehicle_data = {
                    'id': vehicle_id,
                    'driver': f'Motorista {vehicle_id}',
                    'total_stops': len(stops),
                    'total_distance': round(distance_km / 2, 2),
                    'estimated_time': f"{total_time_minutes // 60}h {total_time_minutes % 60}min",
                    'start_time': '08:00',
                    'end_time': f"{int(current_time // 60):02d}:{int(current_time % 60):02d}",
                    'stops': stops
                }
                
                route_data['vehicles'].append(vehicle_data)
        
        return route_data
    
    def _get_service_type_from_priority(self, point) -> str:
        """ Converte prioridade do ServicePoint para tipo de serviço """
        priority_map = {
            'EMERGENCY_OBSTETRIC': 'EME',
            'DOMESTIC_VIOLENCE': 'VIO',
            'HORMONAL_MEDICATION': 'MED',
            'POSTPARTUM_CARE': 'POS',
            'REGULAR': 'REG'
        }
        priority_name = point.priority.name
        return priority_map.get(priority_name, 'REG')
    
    def _get_instructions(self, service_type: str) -> str:
        """ Retorna instruções baseadas no tipo de serviço """
        instructions = {
            'EME': '⚠️ EMERGÊNCIA OBSTÉTRICA - Prioridade máxima. Seguir protocolo especial.',
            'VIO': '🔒 VIOLÊNCIA DOMÉSTICA - Protocolo especial de segurança.',
            'MED': '🌡️ MEDICAMENTO HORMONAL - Controle de temperatura obrigatório.',
            'POS': '👶 PÓS-PARTO - Atendimento com cuidado especial.',
            'REG': '📋 ATENDIMENTO REGULAR'
        }
        return instructions.get(service_type, '📋 ATENDIMENTO')
    
    def _get_special_notes(self, point) -> str:
        """ Retorna notas especiais baseadas no ponto """
        notes = {
            'EME': 'Paciente em situação crítica. Agilidade essencial.',
            'VIO': 'Discrição total. Janela de tempo: 8h-10h.',
            'MED': 'Manter refrigeração. Tempo máximo: 120 minutos.',
            'POS': 'Janela de tempo: 9h-11h.',
            'REG': 'Horário comercial: 8h-18h.'
        }
        service_type = self._get_service_type_from_priority(point)
        return notes.get(service_type, 'Seguir protocolo padrão.')


# Exemplo de uso
if __name__ == "__main__":
    integration = RouteDataIntegration()
    
    # Tenta carregar rota mais recente
    route = integration.load_latest_route()
    
    if route:
        print("✅ Rota carregada com sucesso!")
        print(f"Data: {route.get('date')}")
        print(f"Veículos: {len(route.get('vehicles', []))}")
    else:
        print("ℹ️ Nenhuma rota encontrada. Use dados de exemplo.")
