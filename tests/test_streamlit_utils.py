"""
Testes para funções utilitárias do Streamlit
Testa formatação, cálculos e funções auxiliares
"""

import pytest
import sys
import os

# Adicionar diretórios ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'streamlit'))

# Importar diretamente do módulo app_streamlit
import app_streamlit
from src.core.service_points import ServicePriority

# Criar aliases para as funções
format_time = app_streamlit.format_time
get_day_from_minutes = app_streamlit.get_day_from_minutes
create_random_service_points = app_streamlit.create_random_service_points


class TestTimeFormatting:
    """Testes para formatação de tempo"""
    
    def test_format_time_morning(self):
        """Testa formatação de horário da manhã"""
        # 8:00 = 480 minutos
        assert format_time(480) == "08:00"
    
    def test_format_time_afternoon(self):
        """Testa formatação de horário da tarde"""
        # 14:30 = 870 minutos
        assert format_time(870) == "14:30"
    
    def test_format_time_midnight(self):
        """Testa formatação de meia-noite"""
        # 0:00 = 0 minutos
        assert format_time(0) == "00:00"
    
    def test_format_time_end_of_day(self):
        """Testa formatação de fim do dia"""
        # 23:59 = 1439 minutos
        assert format_time(1439) == "23:59"
    
    def test_format_time_next_day(self):
        """Testa formatação de horário no dia seguinte"""
        # 1440 minutos = 24h = volta para 00:00
        assert format_time(1440) == "00:00"
        # 1500 minutos = 25h = 01:00
        assert format_time(1500) == "01:00"


class TestDayCalculation:
    """Testes para cálculo de dia"""
    
    def test_get_day_first_day(self):
        """Testa cálculo do primeiro dia"""
        # Qualquer horário antes de 1440 minutos (24h) é dia 1
        assert get_day_from_minutes(0) == 1
        assert get_day_from_minutes(480) == 1   # 8:00
        assert get_day_from_minutes(1080) == 1  # 18:00
        assert get_day_from_minutes(1439) == 1  # 23:59
    
    def test_get_day_second_day(self):
        """Testa cálculo do segundo dia"""
        # De 1440 a 2879 minutos é dia 2
        assert get_day_from_minutes(1440) == 2  # 00:00 do dia 2
        assert get_day_from_minutes(1920) == 2  # 08:00 do dia 2
        assert get_day_from_minutes(2879) == 2  # 23:59 do dia 2
    
    def test_get_day_third_day(self):
        """Testa cálculo do terceiro dia"""
        # De 2880 a 4319 minutos é dia 3
        assert get_day_from_minutes(2880) == 3  # 00:00 do dia 3
        assert get_day_from_minutes(3360) == 3  # 08:00 do dia 3


class TestServicePointsCreation:
    """Testes para criação de pontos de serviço"""
    
    def test_create_service_points_count(self):
        """Testa se cria o número correto de pontos"""
        n_points = 20
        points = create_random_service_points(n_points)
        
        # Deve criar n_points + 1 (incluindo depósito)
        assert len(points) == n_points + 1
    
    def test_create_service_points_depot(self):
        """Testa se o primeiro ponto é o depósito"""
        points = create_random_service_points(20)
        
        depot = points[0]
        assert depot.id == 0
        assert depot.service_duration == 0.0
    
    def test_create_service_points_has_emergencies(self):
        """Testa se cria pontos de emergência"""
        points = create_random_service_points(20)
        
        emergency_count = sum(
            1 for p in points 
            if p.priority == ServicePriority.EMERGENCY_OBSTETRIC
        )
        
        # Deve ter pelo menos 2 emergências (garantidas)
        assert emergency_count >= 2
    
    def test_create_service_points_has_violence(self):
        """Testa se cria pontos de violência doméstica"""
        points = create_random_service_points(20)
        
        violence_count = sum(
            1 for p in points 
            if p.priority == ServicePriority.DOMESTIC_VIOLENCE
        )
        
        # Deve ter pelo menos 2 pontos de violência (garantidos)
        assert violence_count >= 2
    
    def test_create_service_points_has_medication(self):
        """Testa se cria pontos de medicamento"""
        points = create_random_service_points(20)
        
        medication_count = sum(
            1 for p in points 
            if p.priority == ServicePriority.HORMONAL_MEDICATION
        )
        
        # Deve ter pelo menos 2 pontos de medicamento (garantidos)
        assert medication_count >= 2
    
    def test_create_service_points_has_postpartum(self):
        """Testa se cria pontos de pós-parto"""
        points = create_random_service_points(20)
        
        postpartum_count = sum(
            1 for p in points 
            if p.priority == ServicePriority.POSTPARTUM_CARE
        )
        
        # Deve ter pelo menos 2 pontos de pós-parto (garantidos)
        assert postpartum_count >= 2
    
    def test_create_service_points_unique_ids(self):
        """Testa se todos os pontos têm IDs únicos"""
        points = create_random_service_points(20)
        
        ids = [p.id for p in points]
        unique_ids = set(ids)
        
        # Todos os IDs devem ser únicos
        assert len(ids) == len(unique_ids)
    
    def test_create_service_points_valid_locations(self):
        """Testa se as localizações estão dentro dos limites"""
        points = create_random_service_points(20)
        
        for point in points:
            x, y = point.location
            # Verificar limites (470-1300, 100-700)
            assert 470 <= x <= 1300
            assert 100 <= y <= 700
    
    def test_create_service_points_time_windows(self):
        """Testa se pontos com janela de tempo têm janelas válidas"""
        points = create_random_service_points(20)
        
        for point in points:
            if point.time_window is not None:
                # Janela de tempo deve ter início antes do fim
                assert point.time_window.start_time < point.time_window.end_time
                
                # Janelas devem estar dentro do horário comercial (8h-18h)
                assert point.time_window.start_time >= 480  # 8:00
                assert point.time_window.end_time <= 1080  # 18:00
