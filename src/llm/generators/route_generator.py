"""
Gerador de roteiros detalhados de visitas
"""

from typing import List, Optional
from src.core.service_points import ServicePoint
from src.llm.providers.base import BaseLLMProvider
from src.llm.prompts.route_templates import (
    ROUTE_SYSTEM_MESSAGE,
    ROUTE_GENERATION_TEMPLATE,
    format_points_for_route
)
from src.llm.utils.formatters import route_to_dict
from src.llm.utils.validators import validate_route_response, sanitize_response


class RouteGenerator:
    """ Gera roteiros detalhados de visitas """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """Inicializa gerador de roteiros """
        self.provider = llm_provider
    
    def generate_route_description(self,
                                   route: List[ServicePoint],
                                   start_time: float = 480.0,
                                   speed: float = 60.0,
                                   max_tokens: Optional[int] = 2500) -> str:
        """ Gera descrição detalhada da rota """
        # Converte rota para dicionário
        route_dict = route_to_dict(route, start_time, speed)
        
        # Formata pontos para o prompt
        points_sequence = format_points_for_route(route_dict['points'])
        
        # Monta prompt
        prompt = ROUTE_GENERATION_TEMPLATE.format(
            points_sequence=points_sequence
        )
        
        # Gera roteiro usando LLM
        try:
            roteiro = self.provider.generate_text(
                prompt=prompt,
                system_message=ROUTE_SYSTEM_MESSAGE,
                max_tokens=max_tokens
            )
            
            # Sanitiza resposta
            roteiro = sanitize_response(roteiro)
            
            # Valida resposta
            is_valid, error_msg = validate_route_response(
                roteiro, 
                route_dict['total_stops']
            )
            if not is_valid:
                raise ValueError(f"Roteiro gerado é inválido: {error_msg}")
            
            return roteiro
            
        except Exception as e:
            raise Exception(f"Erro ao gerar roteiro: {str(e)}")
    
    def save_route(self, roteiro: str, filepath: str) -> None:
        """ Salva roteiro em arquivo """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(roteiro)
            print(f"✅ Roteiro salvo em: {filepath}")
        except Exception as e:
            raise Exception(f"Erro ao salvar roteiro: {str(e)}")
