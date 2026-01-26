import streamlit as st
from db import listar_pedidos, criar_pedido, mover_pedido

st.set_page_config(page_title="Fila de Pedidos", layout="wide")

# login simples (sem auth por enquanto, só para identificar ações)
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

st.sidebar.header("Usuário")
st.session_state.usuario = st.sidebar.text_input("Nome", value=st.session_state.usuario).strip()

if not st.session_state.usuario:
    st.info("Digite seu nome no menu lateral para usar o sistema.")
    st.stop()

st.title("Fila de Pedidos")

with st.expander("Criar pedido", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    numero = col1.text_input("Número")
    nome = col2.text_input("Nome/Cliente")
    ESTADOS = [
        "PEDIDO",
        "EM_MONTAGEM",
        "MONTADOS",
        "FATURADO",
        "EMBALADO",
        "RETIRADO",
    ]

    estado = col3.selectbox("Estado", ESTADOS)

    STATUS = [
        "ATIVO",
        "CANCELADO",
    ]

    status = col4.selectbox("Status", STATUS)

    if st.button("Criar"):
        if not numero or not nome:
            st.warning("Preencha número e nome.")
        else:
            criar_pedido(numero, nome, estado, status, st.session_state.usuario)
            st.success("Criado.")

st.divider()

pedidos = listar_pedidos()

# mostrar em colunas por estado (kanban simples)
estados = [
    "PEDIDO",
    "EM_MONTAGEM",
    "MONTADOS",
    "FATURADO",
    "EMBALADO",
    "RETIRADO",
]

cols = st.columns(len(estados))

for i, est in enumerate(estados):
    with cols[i]:
        st.subheader(est)
        for p in [x for x in pedidos if x["estado_atual"] == est]:
            st.caption(f'{p["numero_pedido"]} • {p["status"]}')
            st.write(p["nome_pedido"])

            c1, c2 = st.columns(2)
            with c1:
                if st.button("◀", key=f'back-{p["id"]}'):
                    idx = estados.index(est)
                    if idx > 0:
                        ok = mover_pedido(p["id"], est, estados[idx-1], st.session_state.usuario)
                        if not ok:
                            st.warning("Não moveu (estado mudou).")
                        st.rerun()
            with c2:
                if st.button("▶", key=f'next-{p["id"]}'):
                    idx = estados.index(est)
                    if idx < len(estados)-1:
                        ok = mover_pedido(p["id"], est, estados[idx+1], st.session_state.usuario)
                        if not ok:
                            st.warning("Não moveu (estado mudou).")
                        st.rerun()
            st.divider()
