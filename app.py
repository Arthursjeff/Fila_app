import streamlit as st
from core import init_session, inject_css, gate_login,

st.set_page_config(
    page_title="Sistema de Pedidos",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()
inject_css()

# ====== NÃO LOGADO ======
if not st.session_state.logado:
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] { display: none !important; }
          [data-testid="stSidebarNav"] { display: none !important; }
          button[kind="header"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

    gate_login()
    st.stop()

# ====== LOGADO ======
st.markdown(
    """
    <style>
      [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏠 Sistema de Pedidos")
st.caption(
    f"Logado como **{st.session_state.usuario_logado}** "
    f"({st.session_state.setor_usuario})"
)

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

