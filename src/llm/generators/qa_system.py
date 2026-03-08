"""
Sistema de perguntas e respostas sobre rotas
"""

from typing import List, Optional, Dict
from src.core.service_points import ServicePoint
from src.llm.providers.base import BaseLLMProvider
from src.llm.prompts.qa_templates import (
    QA_SYSTEM_MESSAGE,
    QA_CONTEXT_TEMPLATE,
    COMMON_QUESTIONS,
    format_route_context
)
from src.llm.utils.formatters import route_to_dict
from src.llm.utils.validators import validate_qa_response, sanitize_response


class QASystem:
    """ Sistema de perguntas e respostas sobre rotas otimizadas """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """ Inicializa sistema de Q&A """
        self.provider = llm_provider
        self.route_context = None
        self.conversation_history = []
    
    def set_route(self,
                  route: List[ServicePoint],
                  start_time: float = 480.0,
                  speed: float = 60.0) -> None:
        """ Define rota para o sistema de Q&A """
        # Converte rota para dicionário
        route_dict = route_to_dict(route, start_time, speed)
        
        # Formata contexto
        self.route_context = format_route_context(route_dict)
        
        # Limpa histórico de conversação
        self.conversation_history = []
        
        print("✅ Rota carregada no sistema de Q&A")
    
    def ask(self, 
            question: str,
            max_tokens: Optional[int] = 500) -> str:
        """ Faz pergunta sobre a rota """
        if self.route_context is None:
            raise ValueError(
                "Rota não definida. Use set_route() primeiro."
            )
        
        # Monta prompt com contexto
        prompt = QA_CONTEXT_TEMPLATE.format(
            route_context=self.route_context,
            user_question=question
        )
        
        # Gera resposta
        try:
            resposta = self.provider.generate_text(
                prompt=prompt,
                system_message=QA_SYSTEM_MESSAGE,
                max_tokens=max_tokens
            )
            
            # Sanitiza resposta
            resposta = sanitize_response(resposta)
            
            # Valida resposta
            is_valid, error_msg = validate_qa_response(resposta)
            if not is_valid:
                raise ValueError(f"Resposta inválida: {error_msg}")
            
            # Adiciona ao histórico
            self.conversation_history.append({
                'question': question,
                'answer': resposta
            })
            
            return resposta
            
        except Exception as e:
            raise Exception(f"Erro ao processar pergunta: {str(e)}")
    
    def ask_common_question(self, question_key: str) -> str:
        """ Faz uma pergunta comum pré-definida """
        if question_key not in COMMON_QUESTIONS:
            available = ", ".join(COMMON_QUESTIONS.keys())
            raise ValueError(
                f"Pergunta '{question_key}' não encontrada. "
                f"Disponíveis: {available}"
            )
        
        question = COMMON_QUESTIONS[question_key]
        return self.ask(question)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """ Retorna histórico de conversação """
        return self.conversation_history.copy()
    
    def clear_history(self) -> None:
        """ Limpa histórico de conversação """
        self.conversation_history = []
        print("✅ Histórico limpo")
