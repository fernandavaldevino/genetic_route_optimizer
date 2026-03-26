"""
Módulo para processar atualizações do Telegram via webhook
Versão otimizada para deploy no GCP (sem polling)
"""

import os
import sys
import asyncio
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
        
        # Manter referência persistente para evitar garbage collection
        self._bot_instance = RouteAssistantBot(self.token, use_real_data=True)
        
        # Copiar todos os handlers configurados
        self.app.add_handler(CommandHandler("start", self._bot_instance.start_command))
        self.app.add_handler(CommandHandler("help", self._bot_instance.help_command))
        self.app.add_handler(CommandHandler("rota", self._bot_instance.route_command))
        self.app.add_handler(CommandHandler("paradas", self._bot_instance.stops_command))
        self.app.add_handler(CommandHandler("proxima", self._bot_instance.next_stop_command))
        self.app.add_handler(CommandHandler("instrucoes", self._bot_instance.instructions_command))
        self.app.add_handler(CommandHandler("iniciar_rota", self._bot_instance.start_route_command))
        self.app.add_handler(CommandHandler("concluido", self._bot_instance.complete_stop_command))
        self.app.add_handler(CommandHandler("concluir_rota", self._bot_instance.finish_route_command))
        self.app.add_handler(CommandHandler("encerrar_rota", self._bot_instance.cancel_route_command))
        self.app.add_handler(CommandHandler("recarregar", self._bot_instance.reload_command))
        self.app.add_handler(CallbackQueryHandler(self._bot_instance.button_callback))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._bot_instance.handle_message))
        
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
_webhook_lock = asyncio.Lock()


async def get_webhook_handler() -> WebhookRouteAssistant:
    """ Obtém ou cria a instância global do webhook handler (thread-safe) """
    global _webhook_handler
    
    if _webhook_handler is not None:
        return _webhook_handler

    async with _webhook_lock:
        # Double-check após adquirir o lock
        if _webhook_handler is not None:
            return _webhook_handler

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
