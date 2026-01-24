import streamlit as st
from client_ollama import GmailMCPClient_Ollama
import asyncio

st.set_page_config(
    page_title="Gmail Assistant",
    page_icon="📧",
    layout="wide"
)

# Inicializar cliente
@st.cache_resource
def get_client():
    return GmailMCPClient_Ollama()

client = get_client()

# Titulo
st.title("📧 Gmail Assistant con MCP de JCDiaz")
st.markdown("Asistente inteligente para gestionar tu Gmail usando Ollama")

# Sidebar para mostrar informacion del cliente MCP
with st.sidebar:
    st.header("🚀 Prompts Rápidos")
    
    if st.button("📊 Resumen diario de emails", use_container_width=True):
        st.session_state.use_prompt = "daily_email_summary"
        st.session_state.prompt_params = {}

    st.divider()

    with st.expander("✉️ Redactar email profesional"):
        recipient = st.text_input("Destinatario (opcional)", key="recipient")
        subject = st.text_input("Asunto (opcional)", key="subject")
        if st.button("Usar prompt", key="compose_btn"):
            st.session_state.use_prompt = "compose_professional_email"
            st.session_state.prompt_params = {
                "recipient": recipient,
                "subject": subject
            }

    st.divider()

    st.markdown("### ℹ️ Información del sistema")
    with st.spinner("Cargando info..."):
        info = asyncio.run(client.get_system_info())

    # Mostrar información en desplegables organizados
    with st.expander("🔧 Herramientas disponibles", expanded=False):
        st.caption(f"Total: {len(info['tools'])}")
        for tool in info['tools']:
            st.markdown(f"• `{tool}`")
    
    with st.expander("📦 Recursos estáticos", expanded=False):
        st.caption(f"Total: {len(info['resources'])}")
        for res in info['resources']:
            st.markdown(f"• `{res}`")
    
    with st.expander("📋 Plantillas de recursos", expanded=False):
        st.caption(f"Total: {len(info.get('templates', []))}")
        if info.get('templates'):
            for template in info['templates']:
                st.markdown(f"• `{template}`")
        else:
            st.info("No hay plantillas de recursos disponibles")
    
    with st.expander("💬 Prompts disponibles", expanded=False):
        st.caption(f"Total: {len(info['prompts'])}")
        for prompt in info['prompts']:
            st.markdown(f"• `{prompt}`")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Función para mostrar respuestas con recursos MCP
def display_message(content: str, role: str = "assistant"):
    """Detecta y formatea respuestas que contienen recursos MCP"""
    # Validar que content no sea None o vacío
    if not content or content.strip() == "":
        return  # No mostrar nada si está vacío
    
    # Detectar si es una respuesta con recurso MCP (buscar patrones comunes)
    lines = content.split('\n')
    
    # Si es un mensaje de tool, mostrarlo en expander
    if role == "tool":
        # Buscar título en las primeras líneas
        title = "📡 Resultado de herramienta"
        if len(lines) > 0 and lines[0].startswith('# '):
            title = f"📡 {lines[0].replace('# ', '')}"
            content = '\n'.join(lines[1:])
        
        with st.expander(title, expanded=False):
            st.markdown(content)
    # Buscar encabezados de recursos (# Titulo)
    elif len(lines) > 5 and lines[0].startswith('# '):
        # Es un recurso MCP, mostrarlo en expander
        title = lines[0].replace('# ', '')
        rest_content = '\n'.join(lines[1:])
        
        with st.expander(f"📄 {title}", expanded=False):
            st.markdown(rest_content)
    else:
        # Respuesta normal
        st.markdown(content)

# Mostrar historial
for msg in st.session_state.messages:
    msg_role = msg.get("role")
    msg_content = msg.get("content")
    
    # Si es un mensaje tool, mostrarlo bajo el contexto del assistant
    if msg_role == "tool":
        with st.chat_message("assistant"):
            display_message(msg_content, role="tool")
    # Para mensajes de usuario y assistant
    elif msg_role in ["user", "assistant"]:
        # Saltar assistant vacíos (solo con tool_calls)
        if msg_role == "assistant" and (not msg_content or msg_content.strip() == ""):
            continue
        
        with st.chat_message(msg_role):
            display_message(msg_content, role=msg_role)

# Manejar prompts
if "use_prompt" in st.session_state:
    prompt_name = st.session_state.pop("use_prompt")
    params = st.session_state.pop("prompt_params", {})
    
    with st.spinner("Cargando prompt..."):
        prompt_msg = asyncio.run(client.get_prompt_messages(prompt_name, **params))
    
    # Mostrar el mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt_msg["content"]["text"]})
    with st.chat_message("user"):
        st.markdown(prompt_msg["content"]["text"])
    
    # Obtener respuesta del assistant
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = asyncio.run(client.chat_completion(st.session_state.messages))
        # Solo mostrar si hay contenido
        if response and response.strip():
            display_message(response, role="assistant")
    
    # Guardar respuesta solo si no está vacía
    if response and response.strip():
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

# Input de usuario
if prompt := st.chat_input("Escribe tu mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = asyncio.run(client.chat_completion(st.session_state.messages))
        # Solo mostrar si hay contenido
        if response and response.strip():
            display_message(response, role="assistant")
    
    # Guardar respuesta solo si no está vacía
    if response and response.strip():
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.rerun()

# Footer
st.divider()
st.caption("Gmail Assistant powered by MCP & Ollama - by JCDiaz")