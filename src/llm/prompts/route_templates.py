"""
Templates de prompts para geração de roteiros detalhados
"""

ROUTE_SYSTEM_MESSAGE = """
Você é um assistente especializado em criar roteiros de visitas claros e práticos
para equipes de saúde. Transforme sequências numéricas de pontos em roteiros
legíveis e úteis para o dia a dia da equipe.
"""

ROUTE_GENERATION_TEMPLATE = """
Transforme a sequência de pontos abaixo em um ROTEIRO DETALHADO DE VISITAS
que a equipe possa seguir facilmente.

## SEQUÊNCIA DE PONTOS:
{points_sequence}

## INSTRUÇÕES PARA O ROTEIRO:

1. **Cabeçalho**
   - Data e turno
   - Resumo executivo (total de paradas, distância, tempo)

2. **Para cada parada, inclua:**
   - Número da parada (ordem)
   - Horário previsto de chegada
   - Endereço/localização
   - Tipo de atendimento
   - Tempo estimado no local
   - Informações relevantes específicas
   - Distância até próxima parada
   - Tempo de viagem até próxima parada

3. **Destaques Importantes**
   - Marque claramente paradas prioritárias (emergências)
   - Indique paradas com requisitos especiais (temperatura controlada)
   - Sinalize janelas de tempo críticas

4. **Resumo Final**
   - Checklist de conclusão
   - Próximos passos

Formate o roteiro de maneira visual e fácil de seguir.
Use emojis ou símbolos para facilitar identificação rápida:
- 🚨 para emergências
- 🏠 para violência doméstica
- 💊 para medicamentos
- 👶 para pós-parto
- ✓ para regular
"""

def format_points_for_route(points_data: list) -> str:
    """
    Formata lista de pontos para inclusão no prompt.
    
    Args:
        points_data: Lista de dicionários com dados dos pontos
        
    Returns:
        String formatada para o prompt
    """
    formatted_points = []
    
    for i, point in enumerate(points_data, 1):
        point_info = f"""
Parada {i}:
- ID: {point.get('id')}
- Localização: {point.get('location')}
- Tipo: {point.get('service_type')}
- Prioridade: {point.get('priority')}
- Horário previsto: {point.get('arrival_time')}
- Duração do atendimento: {point.get('service_duration')} min
- Requisitos especiais: {point.get('special_requirements', 'Nenhum')}
"""
        if i < len(points_data):
            point_info += f"- Distância até próxima parada: {point.get('distance_to_next', 0):.2f} km\n"
            point_info += f"- Tempo até próxima parada: {point.get('time_to_next', 0):.1f} min\n"
        
        formatted_points.append(point_info)
    
    return "\n".join(formatted_points)