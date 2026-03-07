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
    """
    Gera manuais de instruções baseados em rotas otimizadas.
    
    Exemplo de uso:
        from src.llm.providers import create_llm_provider
        
        provider = create_llm_provider()
        generator = ManualGenerator(provider)
        
        manual = generator.generate_manual(route)
        print(manual)
    """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """
        Inicializa gerador de manuais.
        
        Args:
            llm_provider: Provedor de LLM configurado
        """
        self.provider = llm_provider
    
    def generate_manual(self, 
                       route: List[ServicePoint],
                       start_time: float = 480.0,
                       speed: float = 60.0,
                       max_tokens: Optional[int] = 2000) -> str:
        """
        Gera manual de instruções para a rota.
        
        Args:
            route: Lista de ServicePoint na ordem otimizada
            start_time: Horário de início em minutos (default: 8h)
            speed: Velocidade do veículo em km/h
            max_tokens: Limite de tokens para resposta
            
        Returns:
            Manual de instruções em texto
            
        Raises:
            ValueError: Se manual gerado for inválido
        """
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
    
    def save_manual(self, manual: str, filepath: str) -> None:
        """
        Salva manual em arquivo.
        
        Args:
            manual: Texto do manual
            filepath: Caminho do arquivo (ex: "manual_rota_01.txt")
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(manual)
            print(f"✅ Manual salvo em: {filepath}")
        except Exception as e:
            raise Exception(f"Erro ao salvar manual: {str(e)}")
