import streamlit as st
from db import listar_pedidos, criar_pedido, mover_pedido

st.set_page_config(page_title="Fila de Pedidos", layout="wide")

# ======================
# LOGIN / SESSÃO
# ======================

USUARIOS_POR_SETOR = {
    "VENDAS": ["Amanda", "Arthur", "Carla", "Jaqueline", "Marilene", "Romulo"],
    "MONTAGEM": ["João", "Ricardo", "Marco"],
}

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "setor_usuario" not in st.session_state:
    st.session_state.setor_usuario = None

def tela_login():
    st.title("Login")

    setor = st.selectbox(
        "Setor",
        ["", "VENDAS", "MONTAGEM"],
        key="login_setor"
    )

    usuarios = USUARIOS_POR_SETOR.get(setor, [])
    usuario = st.selectbox(
        "Usuário",
        [""] + usuarios,
        key="login_usuario"
    )

    if st.button("Entrar"):
        if not setor or not usuario:
            st.error("Selecione setor e usuário.")
            return

        st.session_state.setor_usuario = setor
        st.session_state.usuario_logado = usuario
        st.rerun()


if not st.session_state.usuario_logado:
    tela_login()
    st.stop()

st.caption(
    f"Logado como **{st.session_state.usuario_logado}** "
    f"({st.session_state.setor_usuario})"
)

if st.button("Trocar usuário"):
    st.session_state.usuario_logado = None
    st.session_state.setor_usuario = None
    st.rerun()


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
            criar_pedido(numero, nome, estado, status, st.session_state.usuario_logado)
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
                        ok = mover_pedido(p["id"], est, estados[idx-1], st.session_state.usuario_logado
)
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
