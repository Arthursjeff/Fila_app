import streamlit as st
from core import init_session, inject_css, gate_login

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Sistema de Pedidos",
    layout="wide",
)

# ==========================================================
# INIT
# ==========================================================

init_session()
inject_css()

# ==========================================================
# NÃO LOGADO
# ==========================================================

if not st.session_state.logado:
    # Esconde sidebar APENAS visualmente (sem quebrar foco)
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True
    )

    gate_login()
    st.stop()

# ==========================================================
# LOGADO
# ==========================================================

# Sidebar visível novamente
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] { visibility: visible; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🏠 Sistema de Pedidos")
st.caption(
    f"Logado como **{st.session_state.nome_usuario}** "
    f"({st.session_state.setor_usuario})"
)

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.markdown("## 📁 Navegação")

    pagina = st.radio(
        "Ir para:",
        ["Fila de Pedidos", "Criar Pedido"],
        label_visibility="collapsed"
    )

    st.divider()

    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================================
# CONTEÚDO PRINCIPAL
# ==========================================================

if pagina == "Criar Pedido":
    from core import render_criar_pedido
    render_criar_pedido()

else:
    from core import render_fila
    render_fila()
