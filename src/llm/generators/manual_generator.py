"""
Gerador de manuais de instruções para equipe de transporte
"""

from typing import List, Optional
from src.core.service_points import ServicePoint
from src.llm.providers.base import BaseLLMProvider
from src.llm.prompts.manual_templates import (
    MANUAL_SYSTEM_MESSAGE,
    MANUAL_GENERATION_TEMPLATE,
    format_route_for_manual
)
from src.llm.utils.formatters import route_to_dict
from src.llm.utils.validators import validate_manual_response, sanitize_response


class ManualGenerator:
    """ Gera manuais de instruções baseados em rotas otimizadas """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """ Inicializa gerador de manuais """
        self.provider = llm_provider
    

    def generate_manual(self, 
                        route: List[ServicePoint],
                        start_time: float = 480.0,
                        speed: float = 60.0,
                        max_tokens: Optional[int] = 2000) -> str:
        """ Gera manual de instruções para a rota """
        # Converte rota para dicionário estruturado
        route_dict = route_to_dict(route, start_time, speed)
        
        # Formata informações para o prompt
        route_info, service_types = format_route_for_manual(route_dict)
        
        # Monta prompt final
        prompt = MANUAL_GENERATION_TEMPLATE.format(
            route_info=route_info,
            service_types=service_types
        )
        
        # Gera manual usando LLM
        try:
            manual = self.provider.generate_text(
                prompt=prompt,
                system_message=MANUAL_SYSTEM_MESSAGE,
                max_tokens=max_tokens
            )
            
            # Sanitiza resposta
            manual = sanitize_response(manual)
            
            # Valida resposta
            is_valid, error_msg = validate_manual_response(manual)
            if not is_valid:
                raise ValueError(f"Manual gerado é inválido: {error_msg}")
            
            return manual
            
        except Exception as e:
            raise Exception(f"Erro ao gerar manual: {str(e)}")
    

    def generate_single_vehicle_manual(self,
                                       route: List[ServicePoint],
                                       arrival_times: List[float],
                                       total_distance: float,
                                       total_time: float,
                                       max_tokens: Optional[int] = 2000) -> str:
        """ Gera manual para um único veículo (compatibilidade com Streamlit)
            Usa o método generate_manual com os parâmetros apropriados """
        return self.generate_manual(route, start_time=arrival_times[0] if arrival_times else 480.0, max_tokens=max_tokens)
    

    def generate_multi_vehicle_manual(self,
                                      vehicles_data: List[dict],
                                      max_tokens: Optional[int] = 2000) -> str:
        """ Gera manual para múltiplos veículos """
        manuals = []
        for i, vehicle_data in enumerate(vehicles_data, 1):
            route = vehicle_data.get('route', [])
            arrival_times = vehicle_data.get('arrival_times', [])
            
            manual = self.generate_single_vehicle_manual(
                route,
                arrival_times,
                vehicle_data.get('total_distance', 0),
                vehicle_data.get('total_time', 0),
                max_tokens
            )
            manuals.append(f"## VEÍCULO {i}\n\n{manual}")
        
        return "\n\n" + "="*80 + "\n\n".join(manuals)
    

    def generate_priority_summary(self, route: List[ServicePoint], include_emojis: bool = True) -> str:
        """ Gera resumo de prioridades da rota """
        from src.llm.utils.formatters import format_service_priority
        
        # Agrupa pontos por prioridade
        priorities = {}
        for point in route:
            if point.id == 0:  # Pula depósito
                continue
            priority_name = format_service_priority(point.priority)  # Nome legível
            if priority_name not in priorities:
                priorities[priority_name] = {
                    'count': 0,
                    'ids': [],
                    'priority_value': point.priority.value
                }
            priorities[priority_name]['count'] += 1
            priorities[priority_name]['ids'].append(point.id)
        
        # Ordena por prioridade (valor menor = mais importante)
        sorted_priorities = sorted(
            priorities.items(),
            key=lambda x: x[1]['priority_value']
        )
        
        # Monta resumo formatado
        summary = "# RESUMO DE PRIORIDADES\n\n"
        summary += "Distribuição dos atendimentos por ordem de prioridade:\n\n"
        
        for priority_name, data in sorted_priorities:
            count = data['count']
            ids = ', '.join(map(str, data['ids']))
            priority_level = data['priority_value']
            
            # Emoji e descrição por prioridade
            if priority_level == 1:
                icon = "🚨" if include_emojis else "[URGENTE]"
                desc = "(URGENTE - Atender primeiro)"
            elif priority_level == 2:
                icon = "⚠️" if include_emojis else "[ALTA]"
                desc = "(ALTA - Protocolo especial)"
            elif priority_level == 3:
                icon = "❄️" if include_emojis else "[TEMP]"
                desc = "(MÉDIA - Controle de temperatura)"
            elif priority_level == 4:
                icon = "👶" if include_emojis else "[CUIDADO]"
                desc = "(MÉDIA - Cuidados especiais)"
            else:
                icon = "📋" if include_emojis else "[NORMAL]"
                desc = "(NORMAL)"
            
            summary += f"{icon} **{priority_name}** {desc}\n"
            summary += f"\t- {count} atendimento(s)\n"
            summary += f"\t- Pontos: {ids}\n\n"
        
        return summary
    
    def generate_checklist(self, route: List[ServicePoint]) -> str:
        """ Gera checklist pré-itinerário """
        checklist = "# CHECKLIST PRÉ-ITINERÁRIO\n\n"
        checklist += "## Verificações Gerais\n"
        checklist += "- [ ] Veículo abastecido\n"
        checklist += "- [ ] Documentação em ordem\n"
        checklist += "- [ ] Equipamentos de segurança\n\n"
        
        # Verifica necessidades específicas
        needs_temp_control = any(p.requires_temperature_control for p in route if p.id != 0)
        needs_special_protocol = any(p.requires_special_protocol for p in route if p.id != 0)
        
        if needs_temp_control:
            checklist += "## Controle de Temperatura\n"
            checklist += "- [ ] Caixa térmica preparada\n"
            checklist += "- [ ] Gelo/refrigeração adequada\n"
            checklist += "- [ ] Termômetro funcionando\n\n"
        
        if needs_special_protocol:
            checklist += "## Protocolos Especiais\n"
            checklist += "- [ ] Documentação de protocolos revisada\n"
            checklist += "- [ ] Equipamentos especiais verificados\n\n"
        
        # Seção Itinerário removida do checklist
        # (mantida apenas no manual de instruções)
        
        return checklist
    
    def save_manual(self, manual: str, filepath: str) -> None:
        """ Salva manual em arquivo """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(manual)
            print(f"✅ Manual salvo em: {filepath}")
        except Exception as e:
            raise Exception(f"Erro ao salvar manual: {str(e)}")
