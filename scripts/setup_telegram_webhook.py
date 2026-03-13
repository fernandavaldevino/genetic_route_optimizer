#!/usr/bin/env python3
"""
Script para configurar o webhook do Telegram
Deve ser executado após o deploy no GCP para registrar a URL do webhook
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Carregar variáveis de ambiente
load_dotenv(ROOT_DIR / '.env')


async def setup_webhook(webhook_url: str, drop_pending: bool = False):
    """ Configura o webhook do Telegram """
    from telegram import Bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado no .env")
        return False
    
    try:
        bot = Bot(token=token)
        
        print(f"🔧 Configurando webhook do Telegram...")
        print(f"📍 URL: {webhook_url}")
        
        # Configurar webhook
        success = await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=drop_pending,
            max_connections=100,
            allowed_updates=["message", "callback_query"]
        )
        
        if success:
            print("✅ Webhook configurado com sucesso!")
            
            # Verificar configuração
            webhook_info = await bot.get_webhook_info()
            print("\n📊 Informações do Webhook:")
            print(f"  • URL: {webhook_info.url}")
            print(f"  • Atualizações pendentes: {webhook_info.pending_update_count}")
            print(f"  • Conexões máximas: {webhook_info.max_connections}")
            
            if webhook_info.last_error_date:
                print(f"  ⚠️ Último erro: {webhook_info.last_error_message}")
            
            return True
        else:
            print("❌ Falha ao configurar webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao configurar webhook: {e}")
        import traceback
        traceback.print_exc()
        return False


async def delete_webhook():
    """ Remove o webhook do Telegram (volta para polling) """
    from telegram import Bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado no .env")
        return False
    
    try:
        bot = Bot(token=token)
        
        print("🗑️ Removendo webhook do Telegram...")
        success = await bot.delete_webhook(drop_pending_updates=True)
        
        if success:
            print("✅ Webhook removido com sucesso!")
            print("ℹ️ O bot agora pode usar polling novamente")
            return True
        else:
            print("❌ Falha ao remover webhook")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao remover webhook: {e}")
        return False


async def check_webhook():
    """ Verifica o status atual do webhook """
    from telegram import Bot
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado no .env")
        return
    
    try:
        bot = Bot(token=token)
        
        print("🔍 Verificando webhook do Telegram...")
        webhook_info = await bot.get_webhook_info()
        
        if webhook_info.url:
            print("\n✅ Webhook ATIVO:")
            print(f"  • URL: {webhook_info.url}")
            print(f"  • Atualizações pendentes: {webhook_info.pending_update_count}")
            print(f"  • Conexões máximas: {webhook_info.max_connections}")
            print(f"  • Certificado customizado: {webhook_info.has_custom_certificate}")
            
            if webhook_info.last_error_date:
                print(f"\n  ⚠️ Último erro ({webhook_info.last_error_date}):")
                print(f"     {webhook_info.last_error_message}")
        else:
            print("\n❌ Webhook NÃO configurado")
            print("ℹ️ O bot está em modo polling ou não está ativo")
            
    except Exception as e:
        print(f"❌ Erro ao verificar webhook: {e}")


def main():
    """ Função principal """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Gerenciar webhook do Telegram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Configurar webhook para GCP Cloud Run
  python scripts/setup_telegram_webhook.py setup https://seu-app-xyz.run.app/webhook

  # Configurar webhook descartando mensagens pendentes
  python scripts/setup_telegram_webhook.py setup https://seu-app-xyz.run.app/webhook --drop-pending

  # Verificar status do webhook
  python scripts/setup_telegram_webhook.py check

  # Remover webhook (voltar para polling)
  python scripts/setup_telegram_webhook.py delete
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Comando setup
    setup_parser = subparsers.add_parser('setup', help='Configurar webhook')
    setup_parser.add_argument('url', help='URL completa do webhook')
    setup_parser.add_argument(
        '--drop-pending',
        action='store_true',
        help='Descartar atualizações pendentes'
    )
    
    # Comando check
    subparsers.add_parser('check', help='Verificar status do webhook')
    
    # Comando delete
    subparsers.add_parser('delete', help='Remover webhook')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Executar comando
    if args.command == 'setup':
        if not args.url:
            print("❌ ERRO: URL do webhook é obrigatória")
            return
        
        if not args.url.startswith('https://'):
            print("❌ ERRO: URL do webhook deve usar HTTPS")
            return
        
        asyncio.run(setup_webhook(args.url, args.drop_pending))
        
    elif args.command == 'check':
        asyncio.run(check_webhook())
        
    elif args.command == 'delete':
        asyncio.run(delete_webhook())


if __name__ == "__main__":
    main()
