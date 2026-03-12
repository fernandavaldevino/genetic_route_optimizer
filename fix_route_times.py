"""
Script para corrigir o tempo estimado nas rotas salvas
Recalcula o tempo considerando múltiplos dias
"""

import json
from pathlib import Path
from typing import Dict, List


def calculate_correct_time(stops: List[Dict]) -> str:
    """
    Calcula o tempo total correto considerando múltiplos dias
    Agrupa paradas por dia e soma o tempo de trabalho de cada dia
    """
    if not stops:
        return "0h 0min"
    
    # Agrupar paradas por dia
    days = []
    current_day_stops = []
    previous_time_mins = None
    
    for stop in stops:
        time_str = stop.get('time', '08:00')
        hours, mins = map(int, time_str.split(':'))
        stop_time_mins = hours * 60 + mins
        
        # Detectar mudança de dia
        if previous_time_mins is not None and stop_time_mins < previous_time_mins:
            # Salvar dia anterior e começar novo dia
            if current_day_stops:
                days.append(current_day_stops)
            current_day_stops = [stop]
        else:
            current_day_stops.append(stop)
        
        duration_str = stop.get('duration', '0 min')
        duration_mins = int(duration_str.split()[0])
        previous_time_mins = stop_time_mins + duration_mins
    
    # Adicionar último dia
    if current_day_stops:
        days.append(current_day_stops)
    
    # Calcular tempo de cada dia
    total_minutes = 0
    for day_stops in days:
        # Tempo = (fim da última parada) - (início da primeira parada)
        first_time = day_stops[0]['time']
        first_h, first_m = map(int, first_time.split(':'))
        first_mins = first_h * 60 + first_m
        
        last_time = day_stops[-1]['time']
        last_h, last_m = map(int, last_time.split(':'))
        last_mins = last_h * 60 + last_m
        last_duration = int(day_stops[-1]['duration'].split()[0])
        
        day_time = (last_mins + last_duration) - first_mins
        total_minutes += day_time
    
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes}min"


def fix_route_file(filepath: Path) -> bool:
    """
    Corrige o tempo estimado em um arquivo de rota
    """
    try:
        # Carregar arquivo
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Processar cada veículo
        modified = False
        for vehicle in data.get('vehicles', []):
            stops = vehicle.get('stops', [])
            if stops:
                old_time = vehicle.get('estimated_time', 'N/A')
                new_time = calculate_correct_time(stops)
                
                if old_time != new_time:
                    vehicle['estimated_time'] = new_time
                    modified = True
                    print(f"  Veículo {vehicle.get('id')}: {old_time} → {new_time}")
        
        # Salvar se houve modificação
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        
        return False
    
    except Exception as e:
        print(f"  ❌ Erro: {e}")
        return False


def main():
    """
    Processa todos os arquivos de rota
    """
    data_dir = Path(__file__).parent / 'data' / 'routes'
    
    if not data_dir.exists():
        print(f"❌ Diretório não encontrado: {data_dir}")
        return
    
    route_files = sorted(data_dir.glob('route_*.json'))
    
    if not route_files:
        print("ℹ️ Nenhum arquivo de rota encontrado")
        return
    
    print(f"🔍 Encontrados {len(route_files)} arquivos de rota\n")
    
    fixed_count = 0
    for filepath in route_files:
        print(f"📄 Processando: {filepath.name}")
        if fix_route_file(filepath):
            fixed_count += 1
            print(f"  ✅ Corrigido!")
        else:
            print(f"  ℹ️ Nenhuma alteração necessária")
        print()
    
    print(f"\n✨ Concluído! {fixed_count} arquivo(s) corrigido(s)")


if __name__ == "__main__":
    main()
