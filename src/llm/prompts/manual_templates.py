"""
Templates de prompts para geração de manuais de instruções
"""

from src.constants import MANUAL_SYSTEM_MESSAGE

MANUAL_GENERATION_TEMPLATE = """
Com base na rota otimizada abaixo, gere um MANUAL DE INSTRUÇÕES PRÁTICO
para a equipe de transporte. O manual deve ser usado durante o percurso.

## INFORMAÇÕES DA ROTA:
{route_info}

## TIPOS DE ATENDIMENTO NA ROTA:
{service_types}

## INSTRUÇÕES PARA O MANUAL:

1. **Título e Introdução**
	- Título claro do manual
	- Breve introdução sobre a missão do dia
	
	**IMPORTANTE**: Na introdução/missão do dia, NÃO mencione:
	  - Quantidade de paradas/pontos
	  - Quilometragem total
	  - Horário de término
	  - Distâncias específicas
	  
	  Foque apenas em: objetivo geral, tipos de atendimento (sem quantidades), e importância do trabalho.

2. **Preparação Antes de Sair**
	- Checklist de materiais necessários para cada tipo de atendimento
	- Equipamentos de proteção individual (EPIs)
	- Documentação necessária

3. **Instruções Específicas por Tipo de Atendimento**
	Para cada tipo presente na rota, forneça:
	
	**EMERGÊNCIA OBSTÉTRICA (se houver):**
	- Protocolo de abordagem
	- Sinais de alerta a observar
	- Procedimentos de emergência
	- Contatos de suporte
	
	**VIOLÊNCIA DOMÉSTICA (se houver):**
	- Abordagem sensível e empática
	- Protocolo de segurança
	- Como identificar situações de risco
	- Rede de apoio e encaminhamentos
	
	**MEDICAMENTOS HORMONAIS (se houver):**
	- Cuidados com temperatura
	- Instruções de armazenamento
	- Orientações para a paciente
	- Verificação de validade
	
	**ATENDIMENTO PÓS-PARTO (se houver):**
	- Avaliação de sinais vitais
	- Orientações sobre amamentação
	- Sinais de alerta pós-parto
	- Suporte emocional
	
	**ATENDIMENTO REGULAR (se houver):**
	- Procedimentos padrão
	- Documentação necessária

4. **Considerações Importantes**
	- Respeito à privacidade e confidencialidade
	- Comunicação empática
	- Registro adequado de informações
	- Procedimentos em caso de intercorrências

5. **Contatos de Emergência**
	- Central de atendimento
	- Supervisor responsável
	- Serviços de emergência

**IMPORTANTE**: NÃO inclua seção de "Itinerário" NO CHECKLIST de pontos de atendimento.
Essas informações serão adicionadas separadamente.

Gere o manual de forma estruturada, clara e prática.
Use linguagem acessível, mas profissional.
"""

def format_route_for_manual(route_data: dict) -> str:
    """
    Formata dados da rota para inclusão no prompt.
    
    Args:
        route_data: Dicionário com informações da rota
        
    Returns:
        String formatada para o prompt
    """
    route_info = f"""
- Total de paradas: {route_data.get('total_stops', 0)}
- Distância total: {route_data.get('total_distance', 0):.2f} km
- Tempo estimado: {route_data.get('total_time', 0):.1f} minutos
- Horário de início: {route_data.get('start_time', '08:00')}
- Horário previsto de término: {route_data.get('end_time', '18:00')}
"""
    
    service_types = route_data.get('service_types', {})
    types_info = []
    
    type_names = {
        'EMERGENCY_OBSTETRIC': 'Emergências Obstétricas',
        'DOMESTIC_VIOLENCE': 'Casos de Violência Doméstica',
        'HORMONAL_MEDICATION': 'Entrega de Medicamentos Hormonais',
        'POSTPARTUM_CARE': 'Atendimentos Pós-Parto',
        'REGULAR': 'Atendimentos Regulares'
    }
    
    for service_type, count in service_types.items():
        if count > 0:
            name = type_names.get(service_type, service_type)
            types_info.append(f"- {name}: {count} parada(s)")
    
    return route_info, "\n".join(types_info)