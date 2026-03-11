"""
Módulo para gerar QR Code do bot de Telegram
Integração com interface Streamlit
"""

import os
import io
from pathlib import Path
from typing import Optional
import qrcode
from PIL import Image


def generate_telegram_qrcode(bot_username: str, size: int = 300, start_param: str = "veiculo1") -> Optional[bytes]:
    """ Gera QR Code para o bot do Telegram """
    try:
        # URL do bot no Telegram
        bot_url = f"https://t.me/{bot_username}?start={start_param}"
        
        # Criar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(bot_url)
        qr.make(fit=True)
        
        # Criar imagem com cor preta
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Redimensionar
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Converter para bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        return None


def get_bot_username_from_env() -> Optional[str]:
    """ Obtém o username do bot do arquivo .env """
    try:
        # Primeiro tenta obter das variáveis de ambiente já carregadas
        bot_username = os.getenv('TELEGRAM_BOT_USERNAME')
        
        # Se não encontrou, tenta BOT_NAME como alternativa
        if not bot_username:
            bot_username = os.getenv('BOT_NAME')
        
        # Se ainda não encontrou, tenta carregar do .env
        if not bot_username:
            from dotenv import load_dotenv
            
            # Carregar .env do diretório raiz
            root_dir = Path(__file__).parent.parent.parent
            env_path = root_dir / '.env'
            
            # Forçar reload das variáveis
            load_dotenv(env_path, override=True)
            
            # Tentar obter username do bot novamente
            bot_username = os.getenv('TELEGRAM_BOT_USERNAME')
            
            # Tentar BOT_NAME novamente
            if not bot_username:
                bot_username = os.getenv('BOT_NAME')
        
        # Se ainda não tem username, tentar extrair do token
        if not bot_username:
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            if token:
                # Token tem formato: 123456789:ABCdefGHI...
                # O bot_id é a primeira parte antes dos ":"
                # Podemos usar como fallback
                bot_id = token.split(':')[0] if ':' in token else None
                if bot_id:
                    # Retornar um username genérico baseado no ID
                    bot_username = f"bot{bot_id}"
        
        return bot_username
    
    except Exception as e:
        print(f"Erro ao obter username do bot: {e}")
        return None


def render_telegram_qrcode_tab(st):
    """ Renderiza a aba de QR Code do Telegram no Streamlit """
    
    # Verificar se é multi-veículo
    is_multi_vehicle = st.session_state.get('is_multi_vehicle', False)
    
    if is_multi_vehicle:
        st.markdown("#### 📱 Acesso Rápido via Telegram - 2 Veículos")
        st.markdown("Escaneie o QR Code correspondente ao seu veículo para acessar o bot do Telegram.")
    else:
        st.markdown("#### 📱 Acesso Rápido via Telegram")
        st.markdown("Escaneie o QR Code abaixo para acessar o bot do Telegram e obter informações sobre sua rota.")
    
    # Obter username do bot
    bot_username = get_bot_username_from_env()
    
    # Debug: mostrar o que foi encontrado
    if bot_username:
        st.success(f"✅ Bot configurado: @{bot_username}")
    else:
        # Tentar mostrar o que está no .env para debug
        import os
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        username = os.getenv('TELEGRAM_BOT_USERNAME')
        st.error(f"Debug - Token encontrado: {'Sim' if token else 'Não'}")
        st.error(f"Debug - Username encontrado: {'Sim' if username else 'Não'}")
        if username:
            st.error(f"Debug - Username value: '{username}'")
    
    if not bot_username:
        # Mostrar instruções de configuração
        st.warning("⚠️ Bot do Telegram não configurado")
        st.info("""
        **Como configurar o bot:**
        
        1. Crie um bot no Telegram com @BotFather
        2. Adicione as configurações no arquivo `.env` do diretório raiz:
           ```
           TELEGRAM_BOT_TOKEN=seu_token_aqui
           TELEGRAM_BOT_USERNAME=seu_bot_username
           ```
        3. Execute o bot: `python telegram_bot/bot.py`
        4. Reinicie o Streamlit
        
        **Documentação completa:** `telegram_bot/README.md`
        """)
        return
    
    if is_multi_vehicle:
        # MODO 2 VEÍCULOS: Gerar QR Codes separados para cada veículo
        qr_bytes_v1 = generate_telegram_qrcode(bot_username, size=300, start_param="veiculo1")
        qr_bytes_v2 = generate_telegram_qrcode(bot_username, size=300, start_param="veiculo2")
        
        if qr_bytes_v1 and qr_bytes_v2:
            # Exibir 2 QR Codes lado a lado
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            # QR Code Veículo 1
            with col1:
                st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: rgba(0, 150, 0, 0.1); border-radius: 10px; border: 2px solid #009600;'>
                    <h3 style='color: #009600; margin-bottom: 15px;'>🚗 Veículo 1</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibir QR Code com tamanho fixo de 3cm (aproximadamente 113px)
                st.markdown(f"""
                <div style='text-align: center; margin-top: 15px;'>
                    <img src='data:image/png;base64,{__import__('base64').b64encode(qr_bytes_v1).decode()}'
                         style='width: 113px; height: 113px; image-rendering: crisp-edges;'
                         alt='QR Code Veículo 1'/>
                    <p style='font-size: 12px; margin-top: 5px;'>@{bot_username}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Link direto Veículo 1
                bot_url_v1 = f"https://t.me/{bot_username}?start=veiculo1"
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <a href='{bot_url_v1}' target='_blank' style='
                        display: inline-block;
                        background: linear-gradient(135deg, #009600, #00b800);
                        color: white;
                        text-decoration: none;
                        padding: 12px 30px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 4px 15px rgba(0, 150, 0, 0.4);
                        transition: all 0.3s ease;
                    '>
                        📱 Abrir Veículo 1
                    </a>
                </div>
                """, unsafe_allow_html=True)
            
            # QR Code Veículo 2
            with col2:
                st.markdown("""
                <div style='text-align: center; padding: 20px; background-color: rgba(0, 200, 200, 0.1); border-radius: 10px; border: 2px solid #00C8C8;'>
                    <h3 style='color: #00C8C8; margin-bottom: 15px;'>🚗 Veículo 2</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Exibir QR Code com tamanho fixo de 3cm (aproximadamente 113px)
                st.markdown(f"""
                <div style='text-align: center; margin-top: 15px;'>
                    <img src='data:image/png;base64,{__import__('base64').b64encode(qr_bytes_v2).decode()}'
                         style='width: 113px; height: 113px; image-rendering: crisp-edges;'
                         alt='QR Code Veículo 2'/>
                    <p style='font-size: 12px; margin-top: 5px;'>@{bot_username}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Link direto Veículo 2
                bot_url_v2 = f"https://t.me/{bot_username}?start=veiculo2"
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <a href='{bot_url_v2}' target='_blank' style='
                        display: inline-block;
                        background: linear-gradient(135deg, #00C8C8, #00e0e0);
                        color: white;
                        text-decoration: none;
                        padding: 12px 30px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 4px 15px rgba(0, 200, 200, 0.4);
                        transition: all 0.3s ease;
                    '>
                        📱 Abrir Veículo 2
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Erro ao gerar QR Codes para os veículos.")
    
    else:
        # MODO 1 VEÍCULO: Gerar QR Code único
        qr_bytes = generate_telegram_qrcode(bot_username, size=300, start_param="veiculo1")
        
        if qr_bytes:
            # Layout original centralizado
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col2:
                # Exibir QR Code com tamanho fixo de 3cm (aproximadamente 113px)
                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{__import__('base64').b64encode(qr_bytes).decode()}'
                         style='width: 113px; height: 113px; image-rendering: crisp-edges;'
                         alt='QR Code'/>
                    <p style='font-size: 12px; margin-top: 5px;'>@{bot_username}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Link direto com start automático
                bot_url = f"https://t.me/{bot_username}?start=veiculo1"
                st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <a href='{bot_url}' target='_blank' style='
                        display: inline-block;
                        background: linear-gradient(135deg, #0088cc, #00a0e9);
                        color: white;
                        text-decoration: none;
                        padding: 12px 30px;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 16px;
                        box-shadow: 0 4px 15px rgba(0, 136, 204, 0.4);
                        transition: all 0.3s ease;
                    '>
                        📱 Abrir no Telegram
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Erro ao gerar QR Code. Verifique a configuração do bot.")
            return
    
    # Instruções de uso (comum para ambos os modos)
    st.markdown("---")
    st.markdown("### 📋 Como usar:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Via QR Code:**
        1. Abra o app do Telegram no celular
        2. Toque no ícone de busca
        3. Toque no ícone de QR Code
        4. Escaneie o código acima
        5. O bot será iniciado automaticamente
        """)
    
    with col2:
        st.markdown(f"""
        **Via Link Direto:**
        1. Clique no botão "Abrir no Telegram"
        2. Ou procure por `@{bot_username}`
        3. O bot será iniciado automaticamente
        4. Use os comandos ou botões interativos
        """)
    
    # Comandos disponíveis
    st.markdown("---")
    st.markdown("### 🤖 Comandos Disponíveis:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - `/start` - Iniciar o bot
        - `/rota` - Ver rota completa
        - `/paradas` - Número de paradas
        - `/proxima` - Próxima parada
        """)
    
    with col2:
        st.markdown("""
        - `/iniciar_rota` - Iniciar rota do dia
        - `/concluir_rota` - Finalizar rota
        - `/instrucoes` - Instruções gerais
        - `/help` - Ajuda completa
        """)
    
    # Funcionalidades
    st.markdown("---")
    st.markdown("### ✨ Funcionalidades:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📍 Informações de Rota**
        - Rota completa do dia
        - Próxima parada
        - Estatísticas
        """)
    
    with col2:
        st.markdown("""
        **🚨 Alertas**
        - Prioridades
        - Janelas de tempo
        - Instruções especiais
        """)
    
    with col3:
        st.markdown("""
        **💬 Interativo**
        - Botões rápidos
        - Linguagem natural
        - Respostas instantâneas
        """)


# Exemplo de uso standalone
if __name__ == "__main__":
    bot_username = "assistente_rotas_bot"  # Exemplo
    qr_bytes = generate_telegram_qrcode(bot_username)
    
    if qr_bytes:
        # Salvar em arquivo
        with open("telegram_qrcode.png", "wb") as f:
            f.write(qr_bytes)
        print("✅ QR Code gerado: telegram_qrcode.png")
    else:
        print("❌ Erro ao gerar QR Code")
