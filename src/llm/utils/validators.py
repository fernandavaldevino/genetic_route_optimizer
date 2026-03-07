"""
Validadores para respostas da LLM
"""

import re
from typing import Tuple, Optional


def validate_manual_response(response: str) -> Tuple[bool, Optional[str]]:
    """ Valida se resposta da LLM para manual está adequada """
    if not response or len(response.strip()) < 100:
        return False, "Resposta muito curta para ser um manual adequado"
    
    # Verifica se contém seções importantes
    required_sections = [
        r'(?i)(preparação|checklist|materiais)',
        r'(?i)(instruções|procedimentos|protocolo)',
        r'(?i)(contato|emergência|suporte)'
    ]
    
    for pattern in required_sections:
        if not re.search(pattern, response):
            return False, f"Manual não contém seção esperada: {pattern}"
    
    return True, None


def validate_route_response(response: str, expected_stops: int) -> Tuple[bool, Optional[str]]:
    """ Valida se resposta da LLM para roteiro está adequada """
    if not response or len(response.strip()) < 50:
        return False, "Resposta muito curta para ser um roteiro adequado"
    
    # Conta menções de "Parada" ou números de ordem
    stop_mentions = len(re.findall(r'(?i)(parada\s+\d+|\d+\.)', response))
    
    if stop_mentions < expected_stops * 0.8:  # Tolerância de 20%
        return False, f"Roteiro não menciona todas as paradas esperadas ({expected_stops})"
    
    return True, None


def validate_qa_response(response: str) -> Tuple[bool, Optional[str]]:
    """ Valida se resposta da LLM para Q&A está adequada """
    if not response or len(response.strip()) < 10:
        return False, "Resposta muito curta"
    
    # Verifica se não é uma recusa genérica
    refusal_patterns = [
        r'(?i)não posso',
        r'(?i)não tenho informação',
        r'(?i)desculpe, mas'
    ]
    
    for pattern in refusal_patterns:
        if re.search(pattern, response):
            return False, "LLM recusou responder ou não tem informação"
    
    return True, None


def sanitize_response(response: str) -> str:
    """ Remove caracteres indesejados da resposta """
    # Remove múltiplas linhas em branco
    response = re.sub(r'\n{3,}', '\n\n', response)
    
    # Remove espaços no final das linhas
    response = '\n'.join(line.rstrip() for line in response.split('\n'))
    
    # Remove espaços múltiplos
    response = re.sub(r' {2,}', ' ', response)
    
    return response.strip()
