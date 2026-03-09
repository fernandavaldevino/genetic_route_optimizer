"""
Módulo para geração de QR Code para WhatsApp Bot
Permite que motoristas acessem o assistente de rota via WhatsApp
"""

import qrcode
from io import BytesIO
from typing import Optional, Dict, Any
import base64


class WhatsAppQRCodeGenerator:
    """ Gerador de QR Code para WhatsApp Bot """
    
    def __init__(self, phone_number: str = "5581999999999"):
        """ Inicializa o gerador de QR Code """
        self.phone_number = phone_number
    
    def generate_whatsapp_link(self, route_data: Dict[str, Any]) -> str:
        """ Gera link do WhatsApp com mensagem pré-formatada """
        # Extrai informações da rota
        vehicle_id = route_data.get('vehicle_id', 1)
        total_points = route_data.get('total_points', 0)
        total_distance = route_data.get('total_distance', 0)
        
        # Mensagem inicial para o bot
        message = (
            f"🚗 Olá! Sou o motorista do Veículo {vehicle_id}.\n"
            f"Preciso de ajuda com minha rota de hoje.\n"
            f"📍 Total de paradas: {total_points}\n"
            f"📏 Distância total: {total_distance:.1f} km"
        )
        
        # Codifica a mensagem para URL
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Gera link do WhatsApp
        whatsapp_link = f"https://wa.me/{self.phone_number}?text={encoded_message}"
        
        return whatsapp_link
    
    def generate_qrcode(self, route_data: Dict[str, Any], 
                       size: int = 300) -> BytesIO:
        """ Gera QR Code para o link do WhatsApp """
        # Gera o link do WhatsApp
        whatsapp_link = self.generate_whatsapp_link(route_data)
        
        # Cria o QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(whatsapp_link)
        qr.make(fit=True)
        
        # Gera a imagem
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Redimensiona se necessário
        if size != 300:
            img = img.resize((size, size))
        
        # Salva em BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return buffer
    
    def generate_qrcode_base64(self, route_data: Dict[str, Any], 
                              size: int = 300) -> str:
        """ Gera QR Code em formato base64 para exibição em HTML """
        buffer = self.generate_qrcode(route_data, size)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"
    
    def get_bot_instructions(self) -> str:
        """ Retorna instruções sobre como usar o bot do WhatsApp """
        instructions = """
        📱 **Como usar o Bot do WhatsApp:**
        
        1. **Escaneie o QR Code** com a câmera do seu celular
        2. **Abra o WhatsApp** automaticamente
        3. **Envie a mensagem** pré-formatada
        4. **Converse com o bot** para obter ajuda sobre:
           - 📍 Próxima parada da rota
           - ⏰ Horários e janelas de tempo
           - 🚨 Prioridades e emergências
           - 🌡️ Cuidados com medicamentos
           - 📋 Protocolos especiais
           - 🗺️ Navegação e direções
        
        💡 **Comandos úteis:**
        - "Próxima parada" - Mostra a próxima parada
        - "Emergências" - Lista paradas de emergência
        - "Medicamentos" - Cuidados com medicamentos
        - "Horários" - Janelas de tempo importantes
        - "Ajuda" - Lista todos os comandos
        """
        return instructions


class WhatsAppBotAssistant:
    """ Assistente de rota para WhatsApp Bot """
    
    def __init__(self, route_data: Dict[str, Any]):
        """ Inicializa o assistente com dados da rota """
        self.route_data = route_data
        self.current_stop = 0
    
    def get_next_stop(self) -> str:
        """ Retorna informações da próxima parada """
        stops = self.route_data.get('stops', [])
        if self.current_stop >= len(stops):
            return "✅ Todas as paradas foram concluídas!"
        
        stop = stops[self.current_stop]
        return self._format_stop_info(stop, self.current_stop + 1)
    
    def get_emergency_stops(self) -> str:
        """ Lista todas as paradas de emergência """
        stops = self.route_data.get('stops', [])
        emergency_stops = [s for s in stops if s.get('priority') == 1]
        
        if not emergency_stops:
            return "✅ Não há paradas de emergência nesta rota."
        
        response = "🚨 **Paradas de Emergência:**\n\n"
        for i, stop in enumerate(emergency_stops, 1):
            response += f"{i}. {self._format_stop_info(stop, i)}\n"
        
        return response
    
    def get_medication_stops(self) -> str:
        """ Lista paradas com medicamentos que requerem controle de temperatura """
        stops = self.route_data.get('stops', [])
        med_stops = [s for s in stops if s.get('type') == 'MED']
        
        if not med_stops:
            return "✅ Não há entregas de medicamentos nesta rota."
        
        response = "🌡️ **Medicamentos (Controle de Temperatura):**\n\n"
        response += "⚠️ Manter temperatura controlada (máx 120 min)\n\n"
        for i, stop in enumerate(med_stops, 1):
            response += f"{i}. {self._format_stop_info(stop, i)}\n"
        
        return response
    
    def get_time_windows(self) -> str:
        """ Lista paradas com janelas de tempo restritas """
        stops = self.route_data.get('stops', [])
        time_sensitive = [s for s in stops if s.get('time_window')]
        
        if not time_sensitive:
            return "✅ Não há restrições de horário especiais."
        
        response = "⏰ **Janelas de Tempo Importantes:**\n\n"
        for i, stop in enumerate(time_sensitive, 1):
            tw = stop.get('time_window', {})
            response += (
                f"{i}. {stop.get('type', 'N/A')} - "
                f"{tw.get('start', 'N/A')} às {tw.get('end', 'N/A')}\n"
            )
        
        return response
    
    def get_help(self) -> str:
        """ Retorna lista de comandos disponíveis """
        return """
        🤖 **Comandos Disponíveis:**
        
        📍 **Navegação:**
        - "Próxima parada" - Próxima parada da rota
        - "Parada atual" - Informações da parada atual
        - "Resumo da rota" - Visão geral da rota
        
        🚨 **Prioridades:**
        - "Emergências" - Lista paradas de emergência
        - "Medicamentos" - Entregas com controle de temperatura
        - "Horários" - Janelas de tempo importantes
        
        📋 **Informações:**
        - "Protocolos" - Protocolos especiais
        - "Distância" - Distância total da rota
        - "Tempo estimado" - Tempo total estimado
        
        💬 **Outros:**
        - "Ajuda" - Esta mensagem
        - "Contato" - Informações de contato
        """
    
    def _format_stop_info(self, stop: Dict[str, Any], number: int) -> str:
        """ Formata informações de uma parada """
        stop_type = stop.get('type', 'N/A')
        priority = stop.get('priority', 'N/A')
        duration = stop.get('duration', 0)
        arrival = stop.get('arrival_time', 'N/A')
        
        priority_emoji = {
            1: "🔴",
            2: "🟠",
            3: "🔵",
            4: "🟣",
            5: "⚫"
        }.get(priority, "⚪")
        
        return (
            f"{priority_emoji} **Parada {number}** - {stop_type}\n"
            f"   ⏰ Chegada: {arrival}\n"
            f"   ⏱️ Duração: {duration} min\n"
            f"   📊 Prioridade: {priority}"
        )
    
    def process_message(self, message: str) -> str:
        """ Processa mensagem do usuário e retorna resposta """
        message_lower = message.lower().strip()
        
        # Comandos de navegação
        if "proxima" in message_lower or "próxima" in message_lower:
            return self.get_next_stop()
        
        # Comandos de prioridade
        if "emergencia" in message_lower or "emergência" in message_lower:
            return self.get_emergency_stops()
        
        if "medicamento" in message_lower:
            return self.get_medication_stops()
        
        if "horario" in message_lower or "horário" in message_lower:
            return self.get_time_windows()
        
        # Ajuda
        if "ajuda" in message_lower or "help" in message_lower:
            return self.get_help()
        
        # Resposta padrão
        return (
            "🤖 Desculpe, não entendi seu comando.\n"
            "Digite 'Ajuda' para ver os comandos disponíveis."
        )
