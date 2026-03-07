""" Gerador de Respostas para Perguntas em Linguagem Natural sobre Rotas """

from typing import Dict, Any, List
from src.llm.providers.base import BaseLLMProvider
from src.core.service_points import ServicePoint
from src.llm.prompts.route_prompts import (
    build_qa_system_prompt,
    build_qa_context_prompt
)


class QAGenerator:
    """ Gerador de respostas para perguntas sobre rotas otimizadas """
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """ Inicializa o gerador com um provedor LLM """
        self.llm_provider = llm_provider
        self.system_prompt = build_qa_system_prompt()
        self.conversation_history = []
    
    def answer_question(self,
                        question: str,
                        route: List[ServicePoint],
                        arrival_times: List[float],
                        total_distance: float,
                        total_time: float,
                        use_history: bool = True) -> str:
        """ Responde uma pergunta sobre a rota otimizada """
        route_data = {
            'route': route,
            'arrival_times': arrival_times,
            'total_distance': total_distance,
            'total_time': total_time
        }
        
        # Construir prompt contextualizado
        context_prompt = build_qa_context_prompt(route_data, question)
        
        # Usar histórico de conversa, se solicitado
        if use_history and self.conversation_history:
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            messages.extend(self.conversation_history)
            messages.append({"role": "user", "content": context_prompt})
            
            try:
                response = self.llm_provider.generate_chat_response(
                    messages=messages,
                    max_tokens=800
                )
            except Exception as e:
                return f"Erro ao gerar resposta: {str(e)}"
        else:
            # Resposta sem histórico
            try:
                response = self.llm_provider.generate_text(
                    prompt=context_prompt,
                    max_tokens=800,
                    system_message=self.system_prompt
                )
            except Exception as e:
                return f"Erro ao gerar resposta: {str(e)}"
        
        # Adicionar ao histórico
        if use_history:
            self.conversation_history.append({"role": "user", "content": question})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Limitar histórico às últimas 10 interações
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def clear_history(self):
        """ Limpa o histórico de conversação """
        self.conversation_history = []
    
    def get_suggested_questions(self,
                                route: List[ServicePoint]) -> List[str]:
        """ Gera sugestões de perguntas relevantes baseadas na rota """
        # Analisar características da rota
        has_emergency = any(p.priority.value == 1 for p in route if p.id != 0)
        has_violence = any(p.priority.value == 2 for p in route if p.id != 0)
        has_medication = any(p.priority.value == 3 for p in route if p.id != 0)
        has_time_windows = any(p.time_window for p in route if p.id != 0)
        num_stops = len([p for p in route if p.id != 0])
        
        suggestions = [
            "Qual é o próximo atendimento prioritário?",
            f"Quantas paradas temos no total?",
            "Qual é o tempo total estimado da rota?"
        ]
        
        if has_emergency:
            suggestions.append("Quais são os pontos de emergência obstétrica?")
        
        if has_violence:
            suggestions.append("Quais cuidados devo ter nos atendimentos de violência doméstica?")
        
        if has_medication:
            suggestions.append("Como devo transportar os medicamentos hormonais?")
        
        if has_time_windows:
            suggestions.append("Quais pontos têm janelas de tempo restritas?")
        
        suggestions.extend([
            "Qual é a distância total da rota?",
            "Há algum ponto que precisa de atenção especial?"
        ])
        
        return suggestions[:8]  # Retornar 8 sugestões, no máximo
    
    def analyze_route_priorities(self,
                                 route: List[ServicePoint],
                                 arrival_times: List[float]) -> str:
        """ Analisa e explica as prioridades da rota """
        from src.core.service_points import ServicePriority
        
        # Agrupar por prioridade
        priority_info = {}
        for i, point in enumerate(route):
            if point.id == 0:
                continue
            
            priority_name = point.priority.name
            if priority_name not in priority_info:
                priority_info[priority_name] = []
            
            arrival = arrival_times[i] if i < len(arrival_times) else 0
            priority_info[priority_name].append({
                'id': point.id,
                'arrival': f"{int(arrival//60):02d}:{int(arrival%60):02d}"
            })
        
        # Construir texto de contexto
        context_parts = []
        for priority, points in priority_info.items():
            points_str = ", ".join([f"Ponto {p['id']} (chegada {p['arrival']})" for p in points])
            context_parts.append(f"{priority}: {points_str}")
        
        context = "\n".join(context_parts)
        
        prompt = f"""
Analise a seguinte distribuição de prioridades na rota:

{context}

Explique:
1. Por que esta ordem foi escolhida
2. Quais são os pontos mais críticos
3. O que a equipe deve priorizar
4. Possíveis riscos e como mitigá-los

Seja claro e educativo. Máximo 200 palavras.
"""
        
        try:
            analysis = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=600,
                system_message="Você é um especialista explicando decisões de otimização de rotas."
            )
            return analysis
        except Exception as e:
            return f"Erro ao analisar prioridades: {str(e)}"
    
    def explain_time_window_compliance(self,
                                       route: List[ServicePoint],
                                       arrival_times: List[float]) -> str:
        """ Explica o cumprimento das janelas de tempo """
        violations = []
        compliant = []
        
        for i, point in enumerate(route):
            if point.id == 0 or not point.time_window:
                continue
            
            arrival = arrival_times[i] if i < len(arrival_times) else 0
            
            if point.time_window.is_valid_time(arrival):
                compliant.append(f"Ponto {point.id}: chegada {int(arrival//60):02d}:{int(arrival%60):02d} (dentro da janela)")
            else:
                tw_start = point.time_window.start_time
                tw_end = point.time_window.end_time
                violations.append(
                    f"Ponto {point.id}: chegada {int(arrival//60):02d}:{int(arrival%60):02d} "
                    f"(janela: {int(tw_start//60):02d}:{int(tw_start%60):02d} - {int(tw_end//60):02d}:{int(tw_end%60):02d})"
                )
        
        compliant_text = "\n".join(compliant) if compliant else "Nenhum"
        violations_text = "\n".join(violations) if violations else "Nenhuma"
        
        prompt = f"""
Análise de cumprimento de janelas de tempo:

ATENDIMENTOS EM CONFORMIDADE:
{compliant_text}

POSSÍVEIS VIOLAÇÕES:
{violations_text}

Explique:
1. O status geral do cumprimento das janelas de tempo
2. Impacto das violações (se houver)
3. Recomendações para garantir cumprimento
4. Margem de segurança disponível

Seja objetivo e prático. Máximo 200 palavras.
"""
        
        try:
            explanation = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=500,
                system_message="Você é um especialista em gestão de tempo e conformidade."
            )
            return explanation
        except Exception as e:
            return f"Erro ao explicar janelas de tempo: {str(e)}"
    
    def get_emergency_info(self,
                           route: List[ServicePoint],
                           arrival_times: List[float]) -> str:
        """ Retorna informações sobre atendimentos de emergência """
        emergencies = []
        
        for i, point in enumerate(route):
            if point.id == 0:
                continue
            
            if point.priority.value == 1:  # Emergência obstétrica
                arrival = arrival_times[i] if i < len(arrival_times) else 0
                emergencies.append({
                    'id': point.id,
                    'arrival': f"{int(arrival//60):02d}:{int(arrival%60):02d}",
                    'position': i
                })
        
        if not emergencies:
            return "Não há atendimentos de emergência obstétrica nesta rota."
        
        emergencies_text = "\n".join([
            f"Ponto {e['id']}: posição {e['position']} na rota, chegada prevista {e['arrival']}"
            for e in emergencies
        ])
        
        prompt = f"""
Atendimentos de EMERGÊNCIA OBSTÉTRICA na rota:

{emergencies_text}

Forneça:
1. Resumo dos atendimentos de emergência
2. Preparação necessária para cada um
3. Protocolos de segurança
4. Contatos de emergência recomendados
5. O que fazer se houver complicações

Seja detalhado mas conciso. Máximo 300 palavras.
"""
        
        try:
            info = self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=600,
                system_message="Você é um especialista em atendimentos de emergência obstétrica."
            )
            return info
        except Exception as e:
            return f"Erro ao obter informações de emergência: {str(e)}"
