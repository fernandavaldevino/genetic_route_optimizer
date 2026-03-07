""" Gerador de Manual de Instruções para Equipe de Transporte """

from typing import Dict, Any, List, Optional
from src.llm.providers.base import BaseLLMProvider
from src.llm.prompts.route_prompts import (
    build_manual_prompt,
    build_multi_vehicle_manual_prompt
)
from src.core.service_points import ServicePoint


class ManualGenerator:
    """ Gerador de manuais de instruções para equipes de transporte """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """ Inicializa o gerador com um provedor LLM """
        self.llm_provider = llm_provider
    
    def generate_single_vehicle_manual(
        self,
        route: List[ServicePoint],
        arrival_times: List[float],
        total_distance: float,
        total_time: float
    ) -> str:
        """ Gera manual de instruções para operação com um único veículo """
        route_data = {
            'route': route,
            'arrival_times': arrival_times,
            'total_distance': total_distance,
            'total_time': total_time,
            'num_vehicles': 1
        }
        
        prompt = build_manual_prompt(route_data)
        
        try:
            manual = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=4000,
                system_message="Você é um especialista em logística de saúde da mulher, criando manuais profissionais e detalhados."
            )
            return manual
        except Exception as e:
            return f"Erro ao gerar manual: {str(e)}"
    
    def generate_multi_vehicle_manual(
        self,
        vehicles_data: List[Dict[str, Any]]
    ) -> str:
        """ Gera manual de instruções coordenado para operação com múltiplos veículos """
        prompt = build_multi_vehicle_manual_prompt(vehicles_data)
        
        try:
            manual = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=4000,
                system_message="Você é um especialista em logística de saúde da mulher, criando manuais coordenados para operações multi-veículo."
            )
            return manual
        except Exception as e:
            return f"Erro ao gerar manual multi-veículo: {str(e)}"
    
    def generate_priority_summary(
        self,
        route: List[ServicePoint]
    ) -> str:
        """ Gera resumo focado nas prioridades da rota """
        from src.core.service_points import ServicePriority
        
        # Agrupar por prioridade
        priority_groups = {
            ServicePriority.EMERGENCY_OBSTETRIC: [],
            ServicePriority.DOMESTIC_VIOLENCE: [],
            ServicePriority.HORMONAL_MEDICATION: [],
            ServicePriority.POSTPARTUM_CARE: [],
            ServicePriority.REGULAR: []
        }
        
        for point in route:
            if point.id != 0:  # Ignorar depósito
                priority_groups[point.priority].append(point.id)
        
        summary_parts = []
        for priority, points in priority_groups.items():
            if points:
                summary_parts.append(f"{priority.name}: Pontos {', '.join(map(str, points))}")
        
        summary_text = "\n".join(summary_parts)
        
        prompt = f"""
Com base na seguinte distribuição de prioridades na rota:

{summary_text}

Crie um RESUMO EXECUTIVO destacando:

**Principais prioridades da operação**
**Alertas críticos (emergências, janelas de tempo)**
**Recomendações para a equipe**
**Pontos de atenção especial**

FORMATO OBRIGATÓRIO:

Para Principais prioridades:
- Incluir TODAS as prioridades presentes: Emergência Obstétrica, Violência Doméstica, Medicamentos Hormonais, Cuidados Pós-Parto
- Formato: - **Nome da Prioridade:** descrição sem negrito
- APENAS o nome antes dos ":" deve estar em negrito
- A descrição APÓS os ":" deve estar SEM negrito (texto normal)

Exemplos CORRETOS para Principais prioridades:
- **Emergência Obstétrica:** Situações críticas que exigem atenção imediata para garantir a saúde materna e fetal.
- **Violência Doméstica:** Identificação e intervenção rápida em casos de violência para proteger a paciente.
- **Medicamentos Hormonais:** Monitoramento cuidadoso da administração para evitar complicações e garantir eficácia.
- **Cuidados Pós-Parto:** Acompanhamento adequado para a recuperação física e emocional da mãe.

Para Alertas críticos, Recomendações e Pontos de atenção:
- Sub-itens SEM negrito, apenas texto normal
- Exemplo: - Situações de Emergência Obstétrica exigem intervenção imediata para evitar complicações.
- Exemplo: - Implementar protocolos de resposta rápida para casos de Emergência Obstétrica.

NÃO faça:
- **Emergência Obstétrica: Situações críticas que exigem atenção imediata...** (descrição em negrito)
- **Situações de Emergência Obstétrica exigem...** (sub-item em negrito nos outros pontos)

Seja conciso mas completo. Máximo 300 palavras.
"""
        
        try:
            summary = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=500,
                system_message="Você é um especialista em saúde da mulher criando resumos executivos."
            )
            return summary
        except Exception as e:
            return f"Erro ao gerar resumo de prioridades: {str(e)}"
    
    def generate_checklist(
        self,
        route: List[ServicePoint]
    ) -> str:
        """ Gera checklist pré-operação baseado nos tipos de atendimento """
        # Identificar tipos de atendimento presentes
        has_emergency = any(p.priority.value == 1 for p in route if p.id != 0)
        has_violence = any(p.priority.value == 2 for p in route if p.id != 0)
        has_medication = any(p.priority.value == 3 for p in route if p.id != 0)
        has_postpartum = any(p.priority.value == 4 for p in route if p.id != 0)
        
        context = f"""
Esta rota inclui:
- Emergências obstétricas: {'SIM' if has_emergency else 'NÃO'}
- Casos de violência doméstica: {'SIM' if has_violence else 'NÃO'}
- Entrega de medicamentos hormonais: {'SIM' if has_medication else 'NÃO'}
- Cuidados pós-parto: {'SIM' if has_postpartum else 'NÃO'}
"""
        
        prompt = f"""
{context}

Crie um CHECKLIST PRÉ-ITINERÁRIO completo para a equipe verificar antes de iniciar a rota.

O checklist deve incluir:
1. Documentação necessária
2. Equipamentos e materiais (específicos para cada tipo de atendimento presente)
3. Verificações do veículo
4. Comunicação e contatos de emergência
5. Protocolos de segurança
6. Itens específicos para cada tipo de atendimento presente na rota

IMPORTANTE:
- NÃO inclua título ou subtítulo no início (ex: "CHECKLIST PRÉ-ITINERÁRIO:")
- Comece DIRETAMENTE com "1. Documentação necessária"
- Formate sub-itens com indentação (4 espaços) e marcador "-"
- Itens numerados (1., 2., etc) devem estar em negrito
"""
        
        try:
            checklist = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=1000,
                system_message="Você é um especialista em preparação de operações de saúde."
            )
            return checklist
        except Exception as e:
            return f"Erro ao gerar checklist: {str(e)}"
