"""
Módulo para processar atualizações do Telegram via webhook
Versão otimizada para deploy no GCP (sem polling)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Carrega variáveis de ambiente
load_dotenv(ROOT_DIR / '.env')

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)


class WebhookRouteAssistant:
    """
    Versão do bot otimizada para webhook (sem polling).
    Processa atualizações do Telegram recebidas via HTTP POST.
    """
    
    def __init__(self, token: str):
        """ Inicializa o assistente de rotas para webhook """
        self.token = token
        self.app = None
        self._initialized = False
    
    async def initialize(self):
        """ Inicializa a aplicação do bot (apenas uma vez) """
        if self._initialized:
            return
        
        # Criar aplicação sem iniciar polling
        self.app = (
            Application.builder()
            .token(self.token)
            .updater(None)  # Desabilita o updater (não usa polling)
            .build()
        )
        
        # Importar e configurar handlers do bot original
        from telegram_bot.bot import RouteAssistantBot
        
        # Criar instância temporária apenas para copiar os handlers
        temp_bot = RouteAssistantBot(self.token, use_real_data=True)
        
        # Copiar todos os handlers configurados
        self.app.add_handler(CommandHandler("start", temp_bot.start_command))
        self.app.add_handler(CommandHandler("help", temp_bot.help_command))
        self.app.add_handler(CommandHandler("rota", temp_bot.route_command))
        self.app.add_handler(CommandHandler("paradas", temp_bot.stops_command))
        self.app.add_handler(CommandHandler("proxima", temp_bot.next_stop_command))
        self.app.add_handler(CommandHandler("instrucoes", temp_bot.instructions_command))
        self.app.add_handler(CommandHandler("iniciar_rota", temp_bot.start_route_command))
        self.app.add_handler(CommandHandler("concluido", temp_bot.complete_stop_command))
        self.app.add_handler(CommandHandler("concluir_rota", temp_bot.finish_route_command))
        self.app.add_handler(CommandHandler("encerrar_rota", temp_bot.cancel_route_command))
        self.app.add_handler(CommandHandler("recarregar", temp_bot.reload_command))
        self.app.add_handler(CallbackQueryHandler(temp_bot.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, temp_bot.handle_message))
        
        # Inicializar a aplicação
        await self.app.initialize()
        await self.app.start()
        
        self._initialized = True
        print("✅ WebhookRouteAssistant inicializado com sucesso")
    
    async def process_update(self, update_data: Dict):
        """ Processa uma atualização recebida via webhook via JSON """
        if not self._initialized:
            await self.initialize()
        
        # Criar objeto Update a partir dos dados JSON
        update = Update.de_json(update_data, self.app.bot)
        
        # Processar a atualização
        await self.app.process_update(update)
    
    async def shutdown(self):
        """ Encerra a aplicação do bot """
        if self._initialized and self.app:
            await self.app.stop()
            await self.app.shutdown()
            self._initialized = False
            print("✅ WebhookRouteAssistant encerrado")


# Instância global do webhook handler (singleton)
_webhook_handler: Optional[WebhookRouteAssistant] = None


async def get_webhook_handler() -> WebhookRouteAssistant:
    """ Obtém ou cria a instância global do webhook handler """
    global _webhook_handler
    
    if _webhook_handler is None:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN não configurado no .env")
        
        _webhook_handler = WebhookRouteAssistant(token)
        await _webhook_handler.initialize()
    
    return _webhook_handler


async def process_telegram_update(update_data: Dict):
    """ Função helper para processar atualizações do Telegram via JSON """
    handler = await get_webhook_handler()
    await handler.process_update(update_data)
