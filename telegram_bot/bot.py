"""
Bot de Telegram para Assistente de Rotas
Fornece instruções e informações sobre rotas otimizadas para motoristas
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Adiciona o diretório raiz ao path para importar módulos do projeto
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Carrega variáveis de ambiente do diretório raiz
load_dotenv(ROOT_DIR / '.env')

# Importa módulo de integração
try:
    from telegram_bot.route_integration import RouteDataIntegration
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    print("⚠️ Módulo de integração não disponível. Usando dados de exemplo.")


class RouteAssistantBot:
    """ Bot de Telegram para assistência de rotas """
    
    def __init__(self, token: str, use_real_data: bool = True):
        self.token = token
        self.app = Application.builder().token(token).build()
        self._setup_handlers()
        
        # Tenta carregar dados reais se disponível
        self.integration = None
        if use_real_data and INTEGRATION_AVAILABLE:
            try:
                self.integration = RouteDataIntegration()
                loaded_data = self.integration.load_latest_route()
                if loaded_data:
                    self.route_data = loaded_data
                    print("✅ Dados reais de rota carregados!")
                else:
                    print("ℹ️ Nenhuma rota salva. Usando dados de exemplo.")
                    self.route_data = self._load_sample_route_data()
            except Exception as e:
                print(f"⚠️ Erro ao carregar dados reais: {e}")
                print("ℹ️ Usando dados de exemplo.")
                self.route_data = self._load_sample_route_data()
        else:
            # Dados de exemplo
            self.route_data = self._load_sample_route_data()
    
    def _reload_route_data(self):
        """ Recarrega os dados da rota mais recente """
        if self.integration and INTEGRATION_AVAILABLE:
            try:
                loaded_data = self.integration.load_latest_route()
                if loaded_data:
                    self.route_data = loaded_data
                    print("🔄 Dados de rota recarregados!")
                    return True
            except Exception as e:
                print(f"⚠️ Erro ao recarregar dados: {e}")
        return False
    
    def _calculate_end_day(self, vehicle_data: Dict) -> int:
        """ Calcula o dia de término baseado na última parada """
        if not vehicle_data.get('stops'):
            return 1
        
        # Pega o horário de início e da última parada
        start_time = vehicle_data.get('start_time', '08:00')
        last_stop = vehicle_data['stops'][-1]
        last_time = last_stop.get('time', '08:00')
        
        # Converte para minutos
        start_hours, start_mins = map(int, start_time.split(':'))
        start_total_mins = start_hours * 60 + start_mins
        
        last_hours, last_mins = map(int, last_time.split(':'))
        last_total_mins = last_hours * 60 + last_mins
        
        # Calcula o dia baseado nos horários
        current_day = 1
        current_time = start_total_mins
        
        for stop in vehicle_data['stops']:
            stop_time = stop.get('time', '08:00')
            stop_hours, stop_mins = map(int, stop_time.split(':'))
            stop_total_mins = stop_hours * 60 + stop_mins
            
            # Se o horário da parada é menor que o horário atual, passou para o próximo dia
            if stop_total_mins < current_time:
                current_day += 1
            
            current_time = stop_total_mins
        
        return current_day
    
    def _get_vehicle_data(self, context: ContextTypes.DEFAULT_TYPE, vehicle_id: Optional[int] = None):
        """ Obtém dados do veículo específico ou do contexto do usuário """
        # Se vehicle_id não foi especificado, tenta obter do contexto do usuário
        if vehicle_id is None:
            vehicle_id = context.user_data.get('vehicle_id', 1)
        
        # Suporta tanto formato antigo quanto novo
        if "vehicles" in self.route_data:
            # Formato novo (com integração)
            vehicles = self.route_data["vehicles"]
            # Melhorar validação e logging
            if vehicle_id <= len(vehicles):
                return vehicles[vehicle_id - 1]
            elif vehicles:
                print(f"⚠️ vehicle_id={vehicle_id} inválido, usando veículo 1")
                return vehicles[0]
            return None
        else:
            # Formato antigo (dados de exemplo)
            return self.route_data.get(f"vehicle_{vehicle_id}", self.route_data.get("vehicle_1"))
    
    def _load_sample_route_data(self) -> Dict:
        """ Carrega dados de exemplo de rotas """
        return {
            "vehicle_1": {
                "driver": "Motorista 1",
                "total_stops": 12,
                "total_distance": 85.5,
                "estimated_time": "6h 30min",
                "start_time": "08:00",
                "end_time": "14:30",
                "stops": [
                    {
                        "id": 1,
                        "type": "EME",
                        "priority": 1,
                        "address": "Rua das Flores, 123",
                        "time": "08:15",
                        "duration": "30 min",
                        "instructions": "⚠️ EMERGÊNCIA OBSTÉTRICA - Prioridade máxima. Seguir protocolo especial.",
                        "special_notes": "Paciente em trabalho de parto. Agilidade essencial."
                    },
                    {
                        "id": 2,
                        "type": "VIO",
                        "priority": 2,
                        "address": "Av. Central, 456",
                        "time": "09:00",
                        "duration": "45 min",
                        "instructions": "🔒 VIOLÊNCIA DOMÉSTICA - Protocolo especial de segurança.",
                        "special_notes": "Discrição total. Janela de tempo: 8h-10h."
                    },
                    {
                        "id": 3,
                        "type": "MED",
                        "priority": 3,
                        "address": "Rua do Comércio, 789",
                        "time": "10:00",
                        "duration": "10 min",
                        "instructions": "🌡️ MEDICAMENTO HORMONAL - Controle de temperatura obrigatório.",
                        "special_notes": "Manter refrigeração. Tempo máximo: 120 minutos."
                    },
                    {
                        "id": 4,
                        "type": "POS",
                        "priority": 4,
                        "address": "Rua das Palmeiras, 321",
                        "time": "10:30",
                        "duration": "20 min",
                        "instructions": "👶 PÓS-PARTO - Atendimento com cuidado especial.",
                        "special_notes": "Janela de tempo: 9h-11h."
                    },
                    {
                        "id": 5,
                        "type": "REG",
                        "priority": 5,
                        "address": "Av. Principal, 654",
                        "time": "11:00",
                        "duration": "15 min",
                        "instructions": "📋 ATENDIMENTO REGULAR",
                        "special_notes": "Horário comercial: 8h-18h."
                    }
                ]
            },
            "vehicle_2": {
                "driver": "Motorista 2",
                "total_stops": 8,
                "total_distance": 62.3,
                "estimated_time": "5h 15min",
                "start_time": "08:00",
                "end_time": "13:15",
                "stops": []
            }
        }
    
    def _setup_handlers(self):
        """ Configura os handlers do bot """
        # Comandos
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("rota", self.route_command))
        self.app.add_handler(CommandHandler("paradas", self.stops_command))
        self.app.add_handler(CommandHandler("proxima", self.next_stop_command))
        self.app.add_handler(CommandHandler("instrucoes", self.instructions_command))
        self.app.add_handler(CommandHandler("iniciar_rota", self.start_route_command))
        self.app.add_handler(CommandHandler("concluido", self.complete_stop_command))
        self.app.add_handler(CommandHandler("concluir_rota", self.finish_route_command))
        self.app.add_handler(CommandHandler("encerrar_rota", self.cancel_route_command))
        self.app.add_handler(CommandHandler("recarregar", self.reload_command))
        
        # Callback queries (botões inline)
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Mensagens de texto
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /start - Mensagem de boas-vindas """
        # Recarregar dados ao iniciar o bot
        self._reload_route_data()
        
        # Limpar todo o contexto anterior (resetar estado)
        context.user_data.clear()
        
        # Detectar parâmetro de veículo (ex: /start veiculo1 ou /start veiculo2)
        vehicle_id = 1  # Padrão
        vehicle_name = "Veículo 1"
        vehicle_color = "🟢"
        
        if context.args:
            arg = context.args[0].lower()
            if 'veiculo2' in arg or 'vehicle2' in arg or arg == '2':
                vehicle_id = 2
                vehicle_name = "Veículo 2"
                vehicle_color = "🔵"
        
        # Salvar veículo no contexto do usuário (garantir que route_started seja False)
        context.user_data['vehicle_id'] = vehicle_id
        context.user_data['route_started'] = False  # Explicitamente definir como False
        
        # IMPORTANTE: Usar _get_initial_keyboard() diretamente, não _get_keyboard()
        # Isso garante que sempre mostre o menu inicial no /start
        reply_markup = self._get_initial_keyboard()
        
        welcome_message = (
            f"👋 *Bem-vindo ao Assistente de Rotas!*\n\n"
            f"{vehicle_color} *{vehicle_name}*\n\n"
            f"🤖 Sou seu assistente virtual para informações sobre rotas de atendimento.\n\n"
            f"*Comandos Principais:*\n"
            f"🚀 /iniciar\\_rota - Iniciar rota do dia\n"
            f"✅ /concluido - Marcar parada como concluída\n"
            f"➡️ /proxima - Ver próxima parada\n"
            f"🏁 /concluir\\_rota - Finalizar rota\n"
            f"🔄 /recarregar - Recarregar rota mais recente\n\n"
            
            f"*Outros Comandos:*\n"
            f"📍 /rota - Ver rota completa\n"
            f"📊 /paradas - Número de paradas\n"
            f"📦 /instrucoes - Instruções gerais\n"
            f"❓ /help - Ajuda completa\n\n"
            f"💡 *Dica:* Use /iniciar\\_rota para começar!"
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /help - Ajuda """
        help_text = (
            "📚 *AJUDA - Comandos Disponíveis*\n\n"
            "*Comandos de Rota:*\n"
            "🚀 /iniciar\\_rota - Iniciar rota do dia\n"
            "✅ /concluido - Marcar parada como concluída\n"
            "➡️ /proxima - Ver próxima parada\n"
            "🏁 /concluir\\_rota - Finalizar rota do dia\n"
            "🔄 /recarregar - Recarregar rota mais recente\n\n"
            "*Comandos de Consulta:*\n"
            "📍 /rota - Ver rota completa (todas as paradas)\n"
            "📊 /paradas - Número total de paradas\n"
            "📦 /instrucoes - Instruções gerais\n\n"
            "*Tipos de Atendimento:*\n"
            "🔴 EME - Emergência Obstétrica (Prioridade 1)\n"
            "🟠 VIO - Violência Doméstica (Prioridade 2)\n"
            "🔵 MED - Medicamento Hormonal (Prioridade 3)\n"
            "🟣 POS - Pós-Parto (Prioridade 4)\n"
            "⚫ REG - Regular (Prioridade 5)\n\n"
            "*Como Usar:*\n"
            "1️⃣ Use /iniciar\\_rota para começar\n"
            "2️⃣ Use /proxima para ver a parada atual\n"
            "3️⃣ Use /concluido após cada atendimento\n"
            "4️⃣ Use /concluir\\_rota ao finalizar o dia\n"
            "5️⃣ Use /recarregar se houver nova otimização"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    def _get_initial_keyboard(self):
        """ Retorna o teclado inline inicial (antes de iniciar a rota) """
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📍 Ver Rota", callback_data="route"),
                InlineKeyboardButton("🚀 Iniciar Rota", callback_data="start_route"),
            ],
            [
                InlineKeyboardButton("📦 Instruções", callback_data="instructions"),
                InlineKeyboardButton("❓ Ajuda", callback_data="help")
            ]
        ])
    
    def _get_active_keyboard(self, context: ContextTypes.DEFAULT_TYPE = None):
        """ Retorna o teclado inline durante a rota (após iniciar) """
        # Verificar se é a última parada
        is_last_stop = False
        if context:
            vehicle_data = self._get_vehicle_data(context)
            if vehicle_data:
                current_index = context.user_data.get('current_stop_index', 0)
                total_stops = len(vehicle_data['stops'])
                # É a última parada se estamos na penúltima posição (antes de concluir)
                is_last_stop = (current_index == total_stops - 1)
        
        if is_last_stop:
            # Na última parada, mostrar apenas o botão "Concluir Rota"
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🏁 Concluir Rota", callback_data="finish_route")
                ],
                [
                    InlineKeyboardButton("📦 Instruções", callback_data="instructions"),
                    InlineKeyboardButton("❓ Ajuda", callback_data="help")
                ],
                [
                    InlineKeyboardButton("❌ Encerrar Rota", callback_data="cancel_route")
                ]
            ])
        else:
            # Nas outras paradas, mostrar os botões normais
            return InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➡️ Próxima Parada", callback_data="next"),
                    InlineKeyboardButton("✅ Concluir Parada", callback_data="complete")
                ],
                [
                    InlineKeyboardButton("📦 Instruções", callback_data="instructions"),
                    InlineKeyboardButton("❓ Ajuda", callback_data="help")
                ],
                [
                    InlineKeyboardButton("❌ Encerrar Rota", callback_data="cancel_route")
                ]
            ])
    
    def _get_keyboard(self, context: ContextTypes.DEFAULT_TYPE = None):
        """ Retorna o teclado apropriado baseado no estado da rota """
        if context and context.user_data.get('route_started'):
            return self._get_active_keyboard(context)
        return self._get_initial_keyboard()
    
    async def route_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /rota - Mostra rota completa """
        # Recarregar dados antes de mostrar a rota
        self._reload_route_data()
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        vehicle_id = context.user_data.get('vehicle_id', 1)
        vehicle_color = "🟢" if vehicle_id == 1 else "🔵"
        
        # Determinar se é apenas 1 veículo
        num_vehicles = len(self.route_data.get("vehicles", [])) if "vehicles" in self.route_data else len([k for k in self.route_data.keys() if k.startswith("vehicle_")])
        
        # Formatar término previsto
        # Para 1 veículo, calcular o dia; para 2 veículos, usar apenas o horário
        end_time_text = vehicle_data['end_time']
        if num_vehicles == 1:
            # Calcular o dia baseado na última parada
            end_day = self._calculate_end_day(vehicle_data)
            end_time_text = f"{vehicle_data['end_time']} do Dia {end_day}"
        
        route_text = (
            f"{vehicle_color} *ROTA COMPLETA - {vehicle_data['driver']}*\n\n"
            f"📊 *Resumo:*\n"
            f"• Total de paradas: {vehicle_data['total_stops']}\n"
            f"• Distância total: {vehicle_data['total_distance']} km\n"
            f"• Tempo estimado: {vehicle_data['estimated_time']}\n"
            f"• Início: {vehicle_data['start_time']}\n"
            f"• Término previsto: {end_time_text}\n\n"
        )
        
        # Agrupar paradas por dia
        stops_by_day = {}
        current_day = 1
        previous_time_mins = 480  # 08:00 em minutos (início do dia)
        
        for stop in vehicle_data['stops']:
            stop_time = stop.get('time', '08:00')
            stop_hours, stop_mins = map(int, stop_time.split(':'))
            stop_time_mins = stop_hours * 60 + stop_mins
            
            # Se o horário da parada é menor que o horário anterior, passou para o próximo dia
            if stop_time_mins < previous_time_mins:
                current_day += 1
            
            if current_day not in stops_by_day:
                stops_by_day[current_day] = []
            
            stops_by_day[current_day].append(stop)
            previous_time_mins = stop_time_mins
        
        # Se há mais de um dia, mostrar agrupado por dia
        if len(stops_by_day) > 1:
            route_text += f"📍 *Paradas por Dia:*\n\n"
            
            days_sorted = sorted(stops_by_day.keys())
            for idx, day in enumerate(days_sorted):
                route_text += f"📅 *Dia {day}:*\n"
                
                for stop in stops_by_day[day]:
                    priority_emoji = {
                        "EME": "🔴",
                        "VIO": "🟠",
                        "MED": "🔵",
                        "POS": "🟣",
                        "REG": "⚫"
                    }.get(stop['type'], "⚪")
                    
                    route_text += (
                        f"{priority_emoji} *Parada {stop['id']} - {stop['type']}*\n"
                        f"📍 {stop['address']}\n"
                        f"🕐 {stop['time']} ({stop['duration']})\n"
                    )
                
                # Adicionar linha em branco após cada dia (exceto o último)
                if idx < len(days_sorted) - 1:
                    route_text += "\n"
        else:
            # Se é apenas um dia, mostrar normalmente
            route_text += f"📍 *Todas as Paradas:*\n\n"
            
            for stop in vehicle_data['stops']:
                priority_emoji = {
                    "EME": "🔴",
                    "VIO": "🟠",
                    "MED": "🔵",
                    "POS": "🟣",
                    "REG": "⚫"
                }.get(stop['type'], "⚪")
                
                route_text += (
                    f"{priority_emoji} *Parada {stop['id']} - {stop['type']}*\n"
                    f"📍 {stop['address']}\n"
                    f"🕐 {stop['time']} ({stop['duration']})\n"
                )
        
        await update.message.reply_text(route_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def stops_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /paradas - Número de paradas """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        # Conta paradas por tipo
        stop_types = {}
        for stop in vehicle_data['stops']:
            stop_type = stop['type']
            stop_types[stop_type] = stop_types.get(stop_type, 0) + 1
        
        stops_text = (
            f"📊 *RESUMO DE PARADAS*\n\n"
            f"Total: *{vehicle_data['total_stops']} paradas*\n\n"
            f"*Por tipo:*\n"
        )
        
        type_names = {
            "EME": "🔴 Emergências",
            "VIO": "🟠 Violência Doméstica",
            "MED": "🔵 Medicamentos",
            "POS": "🟣 Pós-Parto",
            "REG": "⚫ Regular"
        }
        
        for stop_type, count in sorted(stop_types.items(), key=lambda x: x[1], reverse=True):
            stops_text += f"• {type_names.get(stop_type, stop_type)}: {count}\n"
        
        await update.message.reply_text(stops_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def emergencies_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /emergencias - Lista emergências """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        emergencies = [s for s in vehicle_data['stops'] if s['type'] in ['EME', 'VIO']]
        
        if not emergencies:
            await update.message.reply_text("✅ Nenhuma emergência na rota de hoje!")
            return
        
        emerg_text = f"🚨 *PARADAS DE EMERGÊNCIA* ({len(emergencies)})\n\n"
        
        for stop in emergencies:
            emerg_text += (
                f"{'🔴' if stop['type'] == 'EME' else '🟠'} *Parada {stop['id']}*\n"
                f"📍 {stop['address']}\n"
                f"🕐 {stop['time']}\n"
                f"⚠️ {stop['special_notes']}\n\n"
            )
        
        await update.message.reply_text(emerg_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def start_route_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /iniciar_rota - Inicia a rota do dia """
        # Recarregar dados antes de iniciar a rota
        self._reload_route_data()
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        # Resetar progresso
        context.user_data['current_stop_index'] = 0
        context.user_data['route_started'] = True
        
        # Determinar se é apenas 1 veículo
        num_vehicles = len(self.route_data.get("vehicles", [])) if "vehicles" in self.route_data else len([k for k in self.route_data.keys() if k.startswith("vehicle_")])
        
        # Formatar término previsto
        # Para 1 veículo, calcular o dia; para 2 veículos, usar apenas o horário
        end_time_text = vehicle_data['end_time']
        if num_vehicles == 1:
            # Calcular o dia baseado na última parada
            end_day = self._calculate_end_day(vehicle_data)
            end_time_text = f"{vehicle_data['end_time']} do Dia {end_day}"
        
        start_text = (
            f"🚀 *ROTA INICIADA!*\n\n"
            f"📊 *Resumo do Dia:*\n"
            f"• Total de paradas: {vehicle_data['total_stops']}\n"
            f"• Distância total: {vehicle_data['total_distance']} km\n"
            f"• Tempo estimado: {vehicle_data['estimated_time']}\n"
            f"• Início: {vehicle_data['start_time']}\n"
            f"• Término previsto: {end_time_text}\n\n"
            f"✅ Use /proxima para ver a primeira parada\n"
            f"✅ Use /concluido após cada atendimento"
        )
        
        await update.message.reply_text(start_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def complete_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /concluido - Marca parada como concluída e mostra próxima """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        # Verificar se a rota foi iniciada OU se já há progresso (current_stop_index > 0)
        # Isso evita perder o progresso se o estado route_started for perdido
        route_started = context.user_data.get('route_started', False)
        current_index = context.user_data.get('current_stop_index', 0)
        
        if not route_started and current_index == 0:
            await update.message.reply_text("⚠️ Use /iniciar_rota primeiro para começar!")
            return
        
        # Se há progresso mas route_started é False, restaurar o estado
        if not route_started and current_index > 0:
            context.user_data['route_started'] = True
        
        current_index = context.user_data.get('current_stop_index', 0)
        
        if current_index >= len(vehicle_data['stops']):
            await update.message.reply_text("🎉 *ROTA CONCLUÍDA!*\n\nTodas as paradas foram atendidas. Ótimo trabalho!", parse_mode='Markdown')
            return
        
        # Obter parada atual antes de avançar
        current_stop = vehicle_data['stops'][current_index]
        current_time = current_stop.get('time', '08:00')
        current_hours, current_mins = map(int, current_time.split(':'))
        current_time_mins = current_hours * 60 + current_mins
        
        # Marcar como concluída e avançar
        context.user_data['current_stop_index'] = current_index + 1
        
        completed_text = f"✅ *Atendimento {current_index + 1} concluído!*\n\n"
        
        # Mostrar próxima parada
        if context.user_data['current_stop_index'] < len(vehicle_data['stops']):
            next_stop = vehicle_data['stops'][context.user_data['current_stop_index']]
            next_time = next_stop.get('time', '08:00')
            next_hours, next_mins = map(int, next_time.split(':'))
            next_time_mins = next_hours * 60 + next_mins
            remaining = len(vehicle_data['stops']) - context.user_data['current_stop_index']
            
            # Verificar se mudou de dia (horário da próxima parada é menor que o atual)
            if next_time_mins < current_time_mins:
                # Fim do dia, precisa descansar
                completed_text = (
                    f"✅ Atendimento {current_index + 1} concluído!\n\n"
                    f"🌙 FIM DO DIA DE TRABALHO\n\n"
                    f"✅ Paradas do dia concluídas!\n"
                    f"⏰ Horário de encerramento: {current_time}\n\n"
                    f"😴 Descanse bem!\n"
                    f"O motorista precisa descansar para retomar as entregas no dia seguinte.\n\n"
                    f"📊 Paradas restantes: {remaining}\n"
                    f"📅 Próximo dia: A primeira entrega amanhã será às {next_time}\n\n"
                    f"💡 Use /proxima quando estiver pronto para continuar amanhã"
                )
                # Adicionar return para enviar mensagem com parse_mode correto
                await update.message.reply_text(completed_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
                return
            else:
                # Mesmo dia, continuar normalmente
                priority_emoji = {
                    "EME": "🔴",
                    "VIO": "🟠",
                    "MED": "🔵",
                    "POS": "🟣",
                    "REG": "⚫"
                }.get(next_stop['type'], "⚪")
                
                completed_text += (
                    f"➡️ *PRÓXIMA PARADA ({remaining} restantes)*\n\n"
                    f"{priority_emoji} *Parada {next_stop['id']} - {next_stop['type']}*\n"
                    f"🎯 Prioridade {next_stop['priority']}\n\n"
                    f"📍 *Endereço:*\n{next_stop['address']}\n\n"
                    f"🕐 *Horário:* {next_stop['time']}\n"
                    f"⏱️ *Duração:* {next_stop['duration']}\n\n"
                    f"📋 *Instruções:*\n{next_stop['instructions']}\n\n"
                    f"ℹ️ *Observações:*\n{next_stop.get('special_notes', 'N/A')}\n\n"
                    f"✅ Use /concluido quando terminar"
                )
                # Enviar com Markdown para formatar corretamente
                await update.message.reply_text(completed_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
                return
        else:
            completed_text += "🎉 ROTA CONCLUÍDA!\n\nTodas as paradas foram atendidas!"
        
        # Enviar mensagem
        await update.message.reply_text(completed_text, reply_markup=self._get_keyboard(context))
    
    async def next_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /proxima - Próxima parada """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        if not context.user_data.get('route_started'):
            await update.message.reply_text("⚠️ Use /iniciar_rota primeiro para começar!")
            return
        
        current_index = context.user_data.get('current_stop_index', 0)
        
        if current_index >= len(vehicle_data['stops']):
            await update.message.reply_text("✅ Todas as paradas foram concluídas!")
            return
        
        stop = vehicle_data['stops'][current_index]
        remaining = len(vehicle_data['stops']) - current_index
        
        priority_emoji = {
            "EME": "🔴",
            "VIO": "🟠",
            "MED": "🔵",
            "POS": "🟣",
            "REG": "⚫"
        }.get(stop['type'], "⚪")
        
        next_text = (
            f"➡️ *PRÓXIMA PARADA ({remaining} restantes)*\n\n"
            f"{priority_emoji} *Parada {stop['id']} - {stop['type']}*\n"
            f"🎯 Prioridade {stop['priority']}\n\n"
            f"📍 *Endereço:*\n{stop['address']}\n\n"
            f"🕐 *Horário:* {stop['time']}\n"
            f"⏱️ *Duração:* {stop['duration']}\n\n"
            f"📋 *Instruções:*\n{stop['instructions']}\n\n"
            f"ℹ️ *Observações:*\n{stop.get('special_notes', 'N/A')}\n\n"
            f"✅ Use /concluido quando terminar"
        )
        
        await update.message.reply_text(next_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def instructions_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /instrucoes - Instruções gerais """
        instructions_text = (
            "📦 *INSTRUÇÕES GERAIS DE TRANSPORTE*\n\n"
            "*🔴 Emergências Obstétricas (EME):*\n"
            "• Prioridade máxima\n"
            "• Seguir protocolo especial\n"
            "• Agilidade essencial\n\n"
            "*🟠 Violência Doméstica (VIO):*\n"
            "• Discrição total\n"
            "• Janela de tempo: 8h-10h\n"
            "• Protocolo de segurança\n\n"
            "*🔵 Medicamentos Hormonais (MED):*\n"
            "• Controle de temperatura obrigatório\n"
            "• Manter refrigeração\n"
            "• Tempo máximo: 120 minutos\n\n"
            "*🟣 Pós-Parto (POS):*\n"
            "• Cuidado especial\n"
            "• Janela de tempo: 9h-11h\n\n"
            "*⚫ Regular (REG):*\n"
            "• Horário comercial: 8h-18h\n\n"
            "*⚠️ IMPORTANTE:*\n"
            "• Respeitar ordem de prioridades\n"
            "• Cumprir janelas de tempo\n"
            "• Seguir protocolos especiais\n"
            "• Jornada máxima: 8 horas/dia"
        )
        
        await update.message.reply_text(instructions_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def finish_route_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /concluir_rota - Finaliza a rota do dia """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.")
            return
        
        if not context.user_data.get('route_started'):
            await update.message.reply_text("⚠️ A rota ainda não foi iniciada. Clique em [Iniciar Rota] ou use /iniciar_rota primeiro!")
            return
        
        current_index = context.user_data.get('current_stop_index', 0)
        total_stops = len(vehicle_data['stops'])
        
        # Se estamos na última parada (penúltima posição), concluir automaticamente
        if current_index == total_stops - 1:
            # Marcar a última parada como concluída
            context.user_data['current_stop_index'] = total_stops
        
        # Verificar se todas as paradas foram concluídas
        if current_index < total_stops - 1:
            remaining = total_stops - current_index
            await update.message.reply_text(
                f"⚠️ ATENÇÃO!\n\n"
                f"Ainda restam {remaining} paradas não concluídas.\n\n"
                f"Tem certeza que deseja finalizar a rota?\n"
                f"Use /concluido para marcar as paradas restantes.",
                reply_markup=self._get_keyboard(context)
            )
            return
        
        # Resetar estado da rota
        context.user_data['route_started'] = False
        context.user_data['current_stop_index'] = 0
        
        driver_name = str(vehicle_data.get('driver', 'Motorista'))
        
        finish_text = (
            f"🎉 ROTA FINALIZADA COM SUCESSO!\n\n"
            f"✅ Total de paradas concluídas: {total_stops}\n"
            f"📊 Distância percorrida: {vehicle_data['total_distance']} km\n"
            f"⏱️ Tempo total: {vehicle_data['estimated_time']}\n\n"
            f"👏 Excelente trabalho, {driver_name}!\n\n"
            f"💡 Use /iniciar_rota quando estiver pronto para uma nova rota."
        )
        
        await update.message.reply_text(finish_text, reply_markup=self._get_keyboard(context))
    
    async def cancel_route_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /encerrar_rota - Encerra a rota sem concluir todas as paradas """
        vehicle_data = self._get_vehicle_data(context)
        
        if not vehicle_data:
            await update.message.reply_text("❌ Nenhuma rota disponível no momento.", reply_markup=self._get_keyboard(context))
            return
        
        if not context.user_data.get('route_started'):
            await update.message.reply_text("⚠️ Nenhuma rota ativa para encerrar.", reply_markup=self._get_keyboard(context))
            return
        
        # Verificar se já foi solicitada confirmação
        if not context.user_data.get('cancel_confirmation_requested'):
            # Primeira vez - pedir confirmação
            current_index = context.user_data.get('current_stop_index', 0)
            total_stops = len(vehicle_data['stops'])
            completed = current_index
            remaining = total_stops - current_index
            
            # Marcar que a confirmação foi solicitada
            context.user_data['cancel_confirmation_requested'] = True
            
            # Criar teclado de confirmação
            confirmation_keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Sim, Encerrar", callback_data="confirm_cancel"),
                    InlineKeyboardButton("❌ Não, Continuar", callback_data="abort_cancel")
                ]
            ])
            
            confirm_text = (
                f"⚠️ *CONFIRMAÇÃO DE ENCERRAMENTO*\n\n"
                f"Tem certeza que deseja encerrar a rota?\n\n"
                f"📊 *Status Atual:*\n"
                f"✅ Paradas concluídas: {completed}\n"
                f"⏭️ Paradas restantes: {remaining}\n\n"
                f"⚠️ Esta ação não pode ser desfeita!"
            )
            
            await update.message.reply_text(confirm_text, parse_mode='Markdown', reply_markup=confirmation_keyboard)
        else:
            # Confirmação já foi dada - executar encerramento
            current_index = context.user_data.get('current_stop_index', 0)
            total_stops = len(vehicle_data['stops'])
            completed = current_index
            remaining = total_stops - current_index
            
            # Resetar estado da rota
            context.user_data['route_started'] = False
            context.user_data['current_stop_index'] = 0
            context.user_data['cancel_confirmation_requested'] = False
            
            driver_name = str(vehicle_data.get('driver', 'Motorista'))
            
            cancel_text = (
                f"❌ *ROTA ENCERRADA*\n\n"
                f"A rota foi encerrada pelo motorista.\n\n"
                f"📊 *Resumo:*\n"
                f"✅ Paradas concluídas: {completed}\n"
                f"⏭️ Paradas não realizadas: {remaining}\n"
                f"📏 Distância total planejada: {vehicle_data['total_distance']} km\n\n"
                f"👤 Motorista: {driver_name}\n\n"
                f"💡 Use /iniciar\\_rota quando estiver pronto para uma nova rota."
            )
            
            await update.message.reply_text(cancel_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
    
    async def _confirm_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Callback para confirmar o encerramento da rota """
        # Marcar que a confirmação foi dada e chamar cancel_route_command novamente
        context.user_data['cancel_confirmation_requested'] = True
        await self.cancel_route_command(update, context)
    
    async def _abort_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Callback para abortar o encerramento da rota """
        # Limpar flag de confirmação
        context.user_data['cancel_confirmation_requested'] = False
        
        await update.message.reply_text(
            "✅ *Encerramento Cancelado*\n\n"
            "A rota continua ativa.\n\n"
            "💡 Use /proxima para ver a próxima parada.",
            parse_mode='Markdown',
            reply_markup=self._get_keyboard(context)
        )
    
    async def reload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Comando /recarregar - Recarrega os dados da rota mais recente """
        await update.message.reply_text("🔄 Recarregando dados da rota mais recente...")
        
        success = self._reload_route_data()
        
        if success:
            vehicle_data = self._get_vehicle_data(context)
            if vehicle_data:
                # Resetar progresso ao recarregar
                context.user_data['current_stop_index'] = 0
                context.user_data['route_started'] = False
                
                reload_text = (
                    f"✅ *Dados recarregados com sucesso!*\n\n"
                    f"📊 *Nova Rota:*\n"
                    f"• Total de paradas: {vehicle_data['total_stops']}\n"
                    f"• Distância total: {vehicle_data['total_distance']} km\n"
                    f"• Tempo estimado: {vehicle_data['estimated_time']}\n\n"
                    f"💡 Use /iniciar\\_rota para começar a nova rota!"
                )
                await update.message.reply_text(reload_text, parse_mode='Markdown', reply_markup=self._get_keyboard(context))
            else:
                await update.message.reply_text("⚠️ Dados recarregados, mas nenhuma rota disponível.")
        else:
            await update.message.reply_text("❌ Erro ao recarregar dados. Verifique se há rotas salvas em data/routes/")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Processa cliques em botões inline """
        query = update.callback_query
        await query.answer()
        
        # Mapeia callbacks para comandos
        callback_map = {
            "route": self.route_command,
            "instructions": self.instructions_command,
            "start_route": self.start_route_command,
            "complete": self.complete_stop_command,
            "next": self.next_stop_command,
            "help": self.help_command,
            "finish_route": self.finish_route_command,
            "cancel_route": self.cancel_route_command,
            "confirm_cancel": self._confirm_cancel_callback,
            "abort_cancel": self._abort_cancel_callback
        }
        
        handler = callback_map.get(query.data)
        if handler:
            # Criar um objeto Update modificado que simula uma mensagem normal
            # Isso garante que o contexto seja preservado corretamente
            class FakeMessage:
                def __init__(self, original_message, parent_context):
                    self._original = original_message
                    self._context = parent_context
                    self.chat = original_message.chat
                    self.message_id = original_message.message_id
                
                async def reply_text(self, text, **kwargs):
                    # Garantir que o reply_markup seja atualizado com o teclado correto
                    if 'reply_markup' not in kwargs or kwargs['reply_markup'] is None:
                        # Se não foi especificado, usar o teclado baseado no contexto atual
                        kwargs['reply_markup'] = self._parent_bot._get_keyboard(self._context)
                    
                    # Sempre enviar nova mensagem ao invés de editar
                    # Isso garante que mensagens importantes (como conclusão de rota) sejam sempre visíveis
                    await self._original.reply_text(text, **kwargs)
            
            fake_message = FakeMessage(query.message, context)
            fake_message._parent_bot = self  # Adicionar referência ao bot
            
            fake_update = Update(
                update_id=update.update_id,
                message=fake_message
            )
            await handler(fake_update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """ Processa mensagens de texto """
        text = update.message.text.lower()
        
        # Respostas baseadas em palavras-chave
        if any(word in text for word in ['rota', 'caminho', 'trajeto']):
            await self.route_command(update, context)
        elif any(word in text for word in ['parada', 'paradas', 'quantas']):
            await self.stops_command(update, context)
        elif any(word in text for word in ['próxima', 'proxima', 'próximo', 'proximo']):
            await self.next_stop_command(update, context)
        elif any(word in text for word in ['instrução', 'instruções', 'como']):
            await self.instructions_command(update, context)
        elif any(word in text for word in ['ajuda', 'help', 'comandos']):
            await self.help_command(update, context)
        else:
            # Resposta padrão
            await update.message.reply_text(
                "🤔 Desculpe, não entendi sua pergunta.\n\n"
                "Use /help para ver os comandos disponíveis ou escolha uma opção:\n"
                "/rota - Ver rota completa\n"
                "/paradas - Número de paradas\n"
                "/proxima - Próxima parada\n"
                "/instrucoes - Instruções gerais"
            )
    
    def run(self):
        """ Inicia o bot """
        print("🤖 Bot iniciado! Aguardando mensagens...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    # Token do bot (obter com @BotFather no Telegram)
    # Lê do arquivo .env do diretório raiz do projeto
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN:
        print("❌ ERRO: Configure o token do bot!")
        print("\n📝 Passos para configurar:")
        print("1. Fale com @BotFather no Telegram")
        print("2. Crie um novo bot com /newbot")
        print("3. Copie o token recebido")
        print("4. Adicione no arquivo .env do diretório raiz:")
        print("   TELEGRAM_BOT_TOKEN=seu_token_aqui")
        print(f"\n📂 Arquivo .env esperado em: {ROOT_DIR / '.env'}")
        exit(1)
    
    print("🤖 Iniciando Bot de Telegram - Assistente de Rotas")
    print(f"📂 Diretório raiz: {ROOT_DIR}")
    print(f"✅ Token configurado")
    
    bot = RouteAssistantBot(TOKEN)
    bot.run()
