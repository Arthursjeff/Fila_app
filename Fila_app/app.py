import streamlit as st
from core import init_session, inject_css, gate_login

st.set_page_config(page_title="Sistema de Pedidos", layout="wide", initial_sidebar_state="expanded")

# Inicialização global
init_session()
inject_css()
gate_login()

st.title("🏠 Sistema de Pedidos")
st.caption(
    f"Logado como **{st.session_state.usuario_logado}** "
    f"({st.session_state.setor_usuario})"
)

with st.sidebar:
    st.markdown("## 📂 Navegação")

    st.page_link("pages/1_➕_Criar_Pedidos.py", label="➕ Criar Pedido")
    st.page_link("pages/2_📦_Fila_de_Pedidos.py", label="📦 Fila de Pedidos")

    st.divider()

    st.caption(
        f"👤 {st.session_state.usuario_logado} "
        f"({st.session_state.setor_usuario})"
    )



st.markdown("""
Use o menu lateral à esquerda para navegar entre as páginas:
- ➕ Criar Pedido  
- 📋 Fila de Pedidos  
""")
