import streamlit as st
from core import (
    init_session,
    inject_css,
    gate_login,
    render_criar_pedido
)

st.set_page_config(page_title="Criar Pedido", layout="wide")

init_session()
inject_css()
gate_login()

render_criar_pedido()
