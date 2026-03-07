""" Templates de prompts para geração de conteúdo relacionado a rotas otimizadas """

from typing import List, Dict, Any
from src.core.service_points import ServicePoint, ServicePriority


def get_priority_description(priority: ServicePriority) -> str:
    """ Retorna descrição detalhada de cada tipo de prioridade """
    descriptions = {
        ServicePriority.EMERGENCY_OBSTETRIC: "**Emergência Obstétrica** - Atendimento urgente que pode envolver risco de vida",
        ServicePriority.DOMESTIC_VIOLENCE: "**Violência Doméstica** - Atendimento sensível que requer protocolo especial e discrição",
        ServicePriority.HORMONAL_MEDICATION: "**Medicamento Hormonal** - Requer controle rigoroso de temperatura durante transporte",
        ServicePriority.POSTPARTUM_CARE: "**Cuidados Pós-Parto** - Atendimento a puérperas que requer atenção especial",
        ServicePriority.REGULAR: "**Atendimento Regular** - Serviço de rotina sem urgência específica"
    }
    return descriptions.get(priority, "Atendimento não especificado")


def get_priority_instructions(priority: ServicePriority) -> str:
    """ Retorna instruções específicas para cada tipo de prioridade """
    instructions = {
        ServicePriority.EMERGENCY_OBSTETRIC: """
        - Prioridade MÁXIMA - atender imediatamente
        - Verificar se há necessidade de equipamentos médicos especiais
        - Manter comunicação constante com a central
        - Estar preparado para possível necessidade de transporte para hospital
        """,
        ServicePriority.DOMESTIC_VIOLENCE: """
        - Manter DISCRIÇÃO ABSOLUTA durante o atendimento
        - Não fazer perguntas em voz alta que possam comprometer a segurança da paciente
        - Seguir protocolo de segurança estabelecido
        - Respeitar rigorosamente a janela de tempo acordada
        - Ter atenção especial ao comportamento e sinais de desconforto da paciente
        """,
        ServicePriority.HORMONAL_MEDICATION: """
        - Verificar temperatura da caixa térmica antes da entrega
        - Medicamentos devem estar entre 2°C e 8°C
        - Não expor os medicamentos ao sol ou ao calor excessivo
        - Entregar rapidamente após chegada ao local
        - Solicitar assinatura confirmando recebimento em condições adequadas
        """,
        ServicePriority.POSTPARTUM_CARE: """
        - Atendimento sensível a mães recentes
        - Respeitar horários de amamentação e descanso
        - Ser paciente e compreensivo com possíveis atrasos
        - Verificar se há necessidade de orientações adicionais
        """,
        ServicePriority.REGULAR: """
        - Seguir procedimento padrão de atendimento
        - Manter cordialidade e profissionalismo
        - Confirmar identidade da pessoa recebedora antes da entrega
        """
    }
    return instructions.get(priority, "Seguir procedimento padrão")


def build_manual_prompt(route_data: Dict[str, Any]) -> str:
    """ Constrói o prompt para geração de manual de instruções para equipe de transporte """
    route = route_data.get('route', [])
    arrival_times = route_data.get('arrival_times', [])
    total_distance = route_data.get('total_distance', 0)
    total_time = route_data.get('total_time', 0)
    num_vehicles = route_data.get('num_vehicles', 1)
    
    # Agrupar pontos por tipo de prioridade
    from collections import defaultdict
    priority_groups = defaultdict(list)
    
    priority_names_pt = {
        ServicePriority.EMERGENCY_OBSTETRIC: 'Emergência Obstétrica',
        ServicePriority.DOMESTIC_VIOLENCE: 'Violência Doméstica',
        ServicePriority.HORMONAL_MEDICATION: 'Medicamento Hormonal',
        ServicePriority.POSTPARTUM_CARE: 'Cuidados Pós-Parto',
        ServicePriority.REGULAR: 'Atendimento Regular'
    }
    
    for i, point in enumerate(route):
        if point.id == 0:  # Pular depósito
            continue
            
        arrival_time = arrival_times[i] if i < len(arrival_times) else 0
        # Calcular dia e horário
        day = int(arrival_time // 1440) + 1  # 1440 minutos = 1 dia
        time_in_day = arrival_time % 1440
        hours = int(time_in_day // 60)
        minutes = int(time_in_day % 60)
        
        priority_groups[point.priority].append({
            'id': point.id,
            'time': f"{hours:02d}:{minutes:02d} do Dia {day}",
            'duration': point.service_duration
        })
    
    # Construir texto agrupado por tipo
    types_info = []
    for priority in [ServicePriority.EMERGENCY_OBSTETRIC, ServicePriority.DOMESTIC_VIOLENCE,
                     ServicePriority.HORMONAL_MEDICATION, ServicePriority.POSTPARTUM_CARE,
                     ServicePriority.REGULAR]:
        if priority in priority_groups and priority_groups[priority]:
            priority_name = priority_names_pt[priority]
            points = priority_groups[priority]
            points_list = ", ".join([f"Ponto {p['id']}" for p in points])
            
            type_info = f"""
{priority_name}:
- Pontos: {points_list}
- Instruções: {get_priority_instructions(priority)}
"""
            types_info.append(type_info)
    
    types_text = "\n".join(types_info)
    
    # Contar pontos (excluindo depósito)
    num_points = len([p for p in route if p.id != 0])
    
    prompt = f"""
Você é um especialista em logística de saúde da mulher. Crie um MANUAL DE INSTRUÇÕES COMPLETO para a equipe de transporte.

O manual deve começar com o título:
# MANUAL DE INSTRUÇÕES PARA TRANSPORTE - LOGÍSTICA DE SAÚDE DA MULHER

INFORMAÇÕES DA ROTA:
- Total de pontos: {num_points}
- Distância total: {total_distance:.1f} km
- Tempo estimado: {int(total_time // 60)}h{int(total_time % 60):02d}

TIPOS DE ATENDIMENTO PRESENTES NA ROTA:
{types_text}

ESTRUTURA DO MANUAL:

# MANUAL DE INSTRUÇÕES PARA TRANSPORTE - LOGÍSTICA DE SAÚDE DA MULHER

## INTRODUÇÃO:
[Breve texto sobre a missão e importância do trabalho]

## TIPOS DE ATENDIMENTO:

[Para cada tipo de atendimento presente, use o formato:]

**Emergência Obstétrica:**
[Descrição do tipo de atendimento e suas características]

- Instruções Específicas:
    - [instrução 1]
    - [instrução 2]
    - [instrução 3]

[Repita para: Violência Doméstica, Medicamento Hormonal, Cuidados Pós-Parto, Atendimento Regular]

## PRIORIDADES E ALERTAS:
[Emergências, janelas críticas, protocolos especiais]

## IMPREVISTOS:
[Orientações para situações não previstas, contatos de emergência]
"""
    
    return prompt


def build_detailed_itinerary_prompt(route_data: Dict[str, Any]) -> str:
    """ Constrói prompt para geração de roteiro detalhado de visitas para o motorista """
    route = route_data.get('route', [])
    arrival_times = route_data.get('arrival_times', [])
    speed = route_data.get('speed', 60.0)  # Velocidade padrão 60 km/h
    
    # Mapeamento de prioridades para português
    priority_names_pt = {
        'EMERGENCY_OBSTETRIC': 'Emergência Obstétrica',
        'DOMESTIC_VIOLENCE': 'Violência Doméstica',
        'HORMONAL_MEDICATION': 'Medicamento Hormonal',
        'POSTPARTUM_CARE': 'Pós-Parto',
        'REGULAR': 'Atendimento Regular'
    }
    
    # Construir sequência detalhada
    sequence_info = []
    for i in range(len(route)):
        if i == 0:  # Depósito inicial
            sequence_info.append(f"INÍCIO: Depósito (Ponto 0) - Horário de saída: 08:00")
            continue
            
        point = route[i]
        if point.id == 0:  # Retorno ao depósito
            continue
            
        arrival_time = arrival_times[i] if i < len(arrival_times) else 0
        # Calcular dia e horário
        day = int(arrival_time // 1440) + 1
        time_in_day = arrival_time % 1440
        hours = int(time_in_day // 60)
        minutes = int(time_in_day % 60)
        
        # Nome da prioridade em português
        priority_pt = priority_names_pt.get(point.priority.name, point.priority.name)
        
        # Calcular distância e próximo destino
        if i > 0:
            from src.core.service_points import calculate_distance
            prev_point = route[i-1]
            distance_from_prev = calculate_distance(prev_point.location, point.location) * 0.1
            travel_time = (arrival_times[i] - arrival_times[i-1] - prev_point.service_duration) if i < len(arrival_times) else 0
        else:
            distance_from_prev = 0
            travel_time = 0
        
        # Próximo destino
        if i < len(route) - 1:
            next_point = route[i+1]
            next_distance = calculate_distance(point.location, next_point.location) * 0.1
            next_travel_time = next_distance / (speed / 60)  # Converter velocidade para km/min
            next_dest = f"Ponto {next_point.id}"
        else:
            # Calcular retorno ao depósito (ponto 0)
            depot = route[0]
            next_distance = calculate_distance(point.location, depot.location) * 0.1
            next_travel_time = next_distance / (speed / 60)  # Converter velocidade para km/min
            next_dest = "Retorno ao depósito"
        
        sequence_info.append(f"""
Parada {i}: Ponto {point.id}
- Chegada: {hours:02d}:{minutes:02d} do Dia {day}
- Tipo: {priority_pt}
- Distância do ponto anterior: {distance_from_prev:.1f} km
- Tempo de viagem do ponto anterior: {int(travel_time)} minutos
- Tempo de atendimento: {int(point.service_duration)} minutos
- Próximo destino: {next_dest}
- Distância até o próximo ponto: {next_distance:.1f} km
- Tempo de viagem até o próximo ponto: {int(next_travel_time)} minutos
""")
    
    sequence_text = "\n".join(sequence_info)
    
    # Contar total de pontos
    total_points = len([p for p in route if p.id != 0])
    
    # Criar lista de IDs
    all_point_ids = [str(p.id) for p in route if p.id != 0]
    ids_list = ", ".join(all_point_ids)
    
    prompt = f"""
Você é um assistente de logística especializado em saúde da mulher. Crie um ROTEIRO DETALHADO DE VISITAS para o motorista.

INFORMAÇÕES CRÍTICAS:
- Total de pontos: {total_points}
- IDs dos pontos: {ids_list}
- Você DEVE incluir TODOS os {total_points} pontos
- NÃO resuma, NÃO agrupe, NÃO omita NENHUM ponto

SEQUÊNCIA DE PARADAS:
{sequence_text}

INSTRUÇÕES PARA O ROTEIRO:
1. Crie um cabeçalho "RESUMO DA JORNADA:" com:
   - Horário de saída: 08:00
   - Horário estimado de chegada: HH:MM do Dia X (use o horário da última parada)
   - Total de pontos de atendimento: {total_points}
   - Distância total: XX.X km

2. Para CADA UMA DAS {total_points} PARADAS, forneça NA ORDEM:
   - Número sequencial da parada (ex: "PARADA 1: Ponto 2")
   - Horário de chegada previsto: HH:MM do Dia X
   - Tipo de atendimento: Nome em Português (em negrito APENAS se for prioritário)
   - Tempo estimado no local: XX minutos
   - Próximo destino: Ponto X (ou "Retorno ao depósito" se for a última parada)
   - Distância até o próximo ponto: X.X km (incluir distância real mesmo na última parada)
   - Tempo de viagem: XX minutos ou XhXX minutos à velocidade média de {speed} km/h (incluir tempo real mesmo na última parada)
   - Observações importantes: (APENAS se houver janelas de tempo ou cuidados especiais)

3. Destaque visualmente as paradas prioritárias
4. Inclua marcos de tempo importantes (pausas sugeridas, horários críticos)
5. Adicione uma seção final com "PONTOS DE ATENÇÃO"
   - Na seção PONTOS DE ATENÇÃO, mencione TODAS as prioridades: Emergência Obstétrica, Violência Doméstica, Medicamento Hormonal e Pós-Parto

FORMATO OBRIGATÓRIO para tipo de atendimento:
- Tipo de atendimento: **Emergência Obstétrica**
- Tipo de atendimento: **Violência Doméstica**
- Tipo de atendimento: **Medicamento Hormonal**
- Tipo de atendimento: **Pós-Parto**
- Tipo de atendimento: Atendimento Regular

FORMATO OBRIGATÓRIO para tempo de viagem:
- Se menos de 60 minutos: "Tempo de viagem: 35 minutos à velocidade média de {speed} km/h"
- Se 60 minutos ou mais: "Tempo de viagem: 1h15 minutos à velocidade média de {speed} km/h"

REGRA CRÍTICA SOBRE OBSERVAÇÕES:
- Se NÃO houver janelas de tempo ou cuidados especiais, NÃO inclua a linha "Observações importantes"
- NUNCA escreva "Observações importantes: N/A"
- NUNCA escreva "Observações importantes: Nenhuma"
- Simplesmente OMITA o item "Observações importantes" se não houver nada a observar

Exemplo CORRETO (sem observações):
- Tempo de viagem: 28 minutos à velocidade média de {speed} km/h

[próxima parada começa aqui, SEM linha de observações]

Exemplo INCORRETO:
- Tempo de viagem: 28 minutos à velocidade média de {speed} km/h
- Observações importantes: N/A

IMPORTANTE:
- Use "Total de pontos de atendimento" ao invés de "Total de paradas"
- Coloque prioridades em **negrito** (Emergência, Violência, Medicamento, Pós-Parto)
- NÃO coloque "Atendimento Regular" em negrito
- NÃO coloque "Observações importantes" em negrito
- "Distância até o próximo ponto" ANTES de "Tempo de viagem"
- Tempo de viagem com velocidade média de {speed} km/h
- Na ÚLTIMA parada, inclua distância e tempo de retorno ao depósito (não deixe 0.0 km ou 0 minutos)
- Use formato de horário "HH:MM do Dia X"
- Confirme que listou TODOS os IDs: {ids_list}

O roteiro deve ser fácil de seguir durante a condução, com informações claras e objetivas.
"""
    
    return prompt


def build_qa_system_prompt() -> str:
    """ Constrói o prompt de sistema para o assistente de perguntas e respostas sobre a rota """
    return """
Você é um assistente especializado em otimização de rotas para atendimentos de saúde da mulher.
Você tem acesso às informações sobre a rota otimizada e pode responder perguntas sobre:

- Ordem de atendimentos e prioridades
- Horários de chegada e janelas de tempo
- Tipos de atendimento e suas características
- Distâncias e tempos de viagem
- Protocolos especiais e cuidados necessários
- Estatísticas da rota (total de pontos, distância, tempo)
- Próximo destino e tempo estimado de chegada

CONTEXTO IMPORTANTE:
- Emergências obstétricas têm prioridade MÁXIMA
- Atendimentos de violência doméstica requerem discrição absoluta
- Medicamentos hormonais precisam de controle de temperatura (2-8°C)
- Cuidados pós-parto requerem sensibilidade e paciência
- Responda baseado APENAS nas informações fornecidas sobre a rota

Responda de forma clara, objetiva e profissional.
Se a pergunta for sobre um ponto específico, forneça todos os detalhes relevantes.
Se não tiver informação suficiente, seja honesto e sugira como obter a informação.
IMPORTANTE: Não assuma informações que não foram fornecidas no contexto da rota.
"""


def build_qa_context_prompt(route_data: Dict[str, Any], question: str) -> str:
    """ Constrói o prompt contextualizado para responder perguntas sobre a rota """
    route = route_data.get('route', [])
    arrival_times = route_data.get('arrival_times', [])
    total_distance = route_data.get('total_distance', 0)
    total_time = route_data.get('total_time', 0)
    
    # Construir contexto da rota
    route_context = f"""
INFORMAÇÕES DA ROTA OTIMIZADA:
- Total de pontos: {len([p for p in route if p.id != 0])}
- Distância total: {total_distance:.1f} km
- Tempo total: {int(total_time // 60)}h{int(total_time % 60):02d}

SEQUÊNCIA DE ATENDIMENTOS:
"""
    
    for i, point in enumerate(route):
        if point.id == 0:
            continue
            
        arrival_time = arrival_times[i] if i < len(arrival_times) else 0
        hours = int(arrival_time // 60)
        minutes = int(arrival_time % 60)
        
        route_context += f"""
Ponto {point.id}:
- Posição na rota: {i}
- Tipo: {get_priority_description(point.priority)}
- Chegada prevista: {hours:02d}:{minutes:02d}
- Tempo de atendimento: {point.service_duration} min
"""
        
        if point.time_window:
            route_context += f"- Janela de tempo: {int(point.time_window.start_time//60):02d}:{int(point.time_window.start_time%60):02d} - {int(point.time_window.end_time//60):02d}:{int(point.time_window.end_time%60):02d}\n"
    
    prompt = f"""
{route_context}

PERGUNTA DO USUÁRIO:
{question}

Responda a pergunta de forma clara e objetiva, usando as informações da rota acima.
Se a pergunta envolver prioridades, destaque os pontos mais importantes.
Se for sobre horários, seja preciso com os tempos.
Se for sobre tipos de atendimento, explique as particularidades.
"""
    
    return prompt


def build_multi_vehicle_manual_prompt(vehicles_data: List[Dict[str, Any]]) -> str:
    """ Constrói prompt para manual de instruções com múltiplos veículos """
    vehicles_info = []
    
    for vehicle_data in vehicles_data:
        vehicle_id = vehicle_data.get('vehicle_id', 0)
        route = vehicle_data.get('route', [])
        total_distance = vehicle_data.get('total_distance', 0)
        total_time = vehicle_data.get('total_time', 0)
        
        points_info = []
        for point in route:
            if point.id == 0:
                continue
            points_info.append(f"  - Ponto {point.id}: {get_priority_description(point.priority)}")
        
        vehicle_info = f"""
VEÍCULO {vehicle_id}:
- Pontos atendidos: {len([p for p in route if p.id != 0])}
- Distância: {total_distance:.1f} km
- Tempo estimado: {int(total_time // 60)}h{int(total_time % 60):02d}
- Sequência:
{chr(10).join(points_info)}
"""
        vehicles_info.append(vehicle_info)
    
    vehicles_text = "\n".join(vehicles_info)
    
    prompt = f"""
Você é um especialista em logística de saúde da mulher. Crie um MANUAL DE INSTRUÇÕES COORDENADO para uma operação com MÚLTIPLOS VEÍCULOS.

INFORMAÇÕES DO ITINERÁRIO:
{vehicles_text}

INSTRUÇÕES PARA O MANUAL:
1. Crie uma introdução explicando a operação coordenada com múltiplos veículos
2. Para CADA VEÍCULO, crie uma seção específica com:
   - Identificação do veículo
   - Resumo da missão (pontos, distância, tempo)
   - Sequência detalhada de atendimentos
   - Instruções específicas para cada parada
   - Pontos de coordenação com outros veículos (se houver)
3. Inclua uma seção de "COORDENAÇÃO ENTRE VEÍCULOS" com:
   - Horários críticos de sincronização
   - Protocolos de comunicação
   - Procedimentos em caso de atraso de um veículo
4. Adicione "PRIORIDADES GERAIS DA OPERAÇÃO"
5. Inclua "CHECKLIST PRÉ-OPERAÇÃO" para cada veículo

O manual deve facilitar a coordenação entre equipes e garantir eficiência na operação.
"""
    
    return prompt
