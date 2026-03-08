"""
Templates de prompts para sistema de perguntas e respostas
"""

from src.constants import QA_SYSTEM_MESSAGE, COMMON_QUESTIONS

QA_CONTEXT_TEMPLATE = """
## CONTEXTO DA ROTA ATUAL:

{route_context}

## PERGUNTA DO USUÁRIO:
{user_question}

## INSTRUÇÕES:
Responda à pergunta do usuário baseando-se exclusivamente nas informações
da rota fornecidas acima. Seja claro e direto.

Se a pergunta for sobre:
- Próximo atendimento: Informe qual é, horário e tipo
- Prioridades: Liste por ordem de prioridade
- Tempo/distância: Forneça estimativas precisas
- Tipo específico: Filtre e liste apenas esse tipo
- Emergências: Destaque e priorize essas informações

Formate a resposta de maneira clara e acionável.
"""

def format_route_context(route_data: dict) -> str:
    """
    Formata contexto da rota para Q&A.
    
    Args:
        route_data: Dados completos da rota
        
    Returns:
        String formatada com contexto
    """
    context = f"""
### RESUMO GERAL:
- Total de paradas: {route_data.get('total_stops', 0)}
- Distância total: {route_data.get('total_distance', 0):.2f} km
- Tempo total estimado: {route_data.get('total_time', 0):.1f} minutos
- Horário de início: {route_data.get('start_time', '08:00')}

### PARADAS POR TIPO:
"""
    
    service_types = route_data.get('service_types', {})
    for service_type, count in service_types.items():
        context += f"- {service_type}: {count}\n"
    
    context += "\n### SEQUÊNCIA DE PARADAS:\n"
    
    for i, point in enumerate(route_data.get('points', []), 1):
        context += f"{i}. {point.get('service_type')} - {point.get('arrival_time')} "
        context += f"(Prioridade: {point.get('priority')})\n"
    
    return context