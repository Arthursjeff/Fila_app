import streamlit as st
from core import init_session, inject_css, gate_login

st.set_page_config(
    page_title="Sistema de Pedidos",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_session()

# ====== ESCONDER SIDEBAR + NAV AUTOMÁTICO ANTES DO LOGIN ======
if not st.session_state.get("logado", False):
    st.markdown(
        """
        <style>
          /* some a sidebar inteira antes do login */
          [data-testid="stSidebar"] { display: none !important; }

          /* some o botão/setinha/hamburger da sidebar */
          button[kind="header"] { display: none !important; }

          /* some o "Page navigation" automático */
          [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )

# CSS geral do app
inject_css()

# ====== LOGIN ======
if not st.session_state.get("logado", False):
    gate_login()
    st.stop()

# ====== LOGADO: esconder APENAS o menu automático do Streamlit ======
st.markdown(
    """
    <style>
      /* remove o menu automático de pages */
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
