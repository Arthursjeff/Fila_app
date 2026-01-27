import streamlit as st
from core import init_session, inject_css, gate_login

st.set_page_config(
    page_title="Sistema de Pedidos",
    layout="wide",
)

# =========================
# INIT
# =========================
init_session()
inject_css()

# =========================
# LOGIN GATE (ABSOLUTO)
# =========================
if not st.session_state.get("logado", False):
    gate_login()
    st.stop()  # ⛔ NADA abaixo renderiza

# =========================
# APP LOGADO
# =========================
st.title("🏠 Sistema de Pedidos")
st.caption(
    f"Logado como **{st.session_state.usuario_logado}** "
    f"({st.session_state.setor_usuario})"
)

# =========================
# SIDEBAR CONTROLADA
# =========================
with st.sidebar:
    st.markdown("## 📁 Navegação")

    if st.button("➕ Criar Pedido", use_container_width=True):
        st.switch_page("pages/1_Criar_Pedidos.py")

    if st.button("📦 Fila de Pedidos", use_container_width=True):
        st.switch_page("pages/2_Fila_de_Pedidos.py")

    st.divider()

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.logado = False
        st.rerun()
