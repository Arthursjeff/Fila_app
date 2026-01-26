import streamlit as st
from db import listar_pedidos, criar_pedido, mover_pedido

st.set_page_config(page_title="Fila de Pedidos", layout="wide")

# ======================
# CONFIG / CONSTANTES
# ======================

# Usuários e senhas (simples por enquanto)
USUARIOS_POR_SETOR = {
    "VENDAS": {
        "Amanda": "1234",
        "Arthur": "1234",
        "Carla": "1234",
        "Jaqueline": "1234",
        "Marilene": "1234",
        "Romulo": "1234",
    },
    "MONTAGEM": {
        "João": "1234",
        "Ricardo": "1234",
        "Marco": "1234",
    },
}

# Estados do banco (precisa existir no enum do Supabase)
ESTADOS_DB = [
    "PEDIDO",
    "EM_MONTAGEM",
    "PROGRAMADOS_IMPORTACAO",
    "MONTADOS",
    "FATURADO",
    "EMBALADO",
    "RETIRADO",
]

ESTADO_LABEL = {
    "PEDIDO": "Pedidos",
    "EM_MONTAGEM": "Em Montagem",
    "PROGRAMADOS_IMPORTACAO": "Programados/Importação",
    "MONTADOS": "Montados",
    "FATURADO": "Faturados",
    "EMBALADO": "Embalados",
    "RETIRADO": "Retirados",
}

# Permissões reais (como no legado)
PERMISSOES_POR_TIPO = {
    "VENDAS": {
        "CRIAR": True,
        "MOVE": {
            "MONTADOS": ["FATURADO"],
        },
    },
    "MONTAGEM": {
        "CRIAR": False,
        "MOVE": {
            "PEDIDO": ["EM_MONTAGEM"],
            "EM_MONTAGEM": ["PROGRAMADOS_IMPORTACAO", "MONTADOS"],
            "PROGRAMADOS_IMPORTACAO": ["MONTADOS"],
            "FATURADO": ["EMBALADO"],
            "EMBALADO": ["RETIRADO"],
        },
    },
}

STATUS_DB = ["ATIVO", "CANCELADO"]

# ======================
# LOGIN / SESSÃO
# ======================

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "setor_usuario" not in st.session_state:
    st.session_state.setor_usuario = None


def tela_login():
    st.title("Login")

    setor = st.selectbox("Setor", ["", "VENDAS", "MONTAGEM"], key="login_setor")
    usuarios = list(USUARIOS_POR_SETOR.get(setor, {}).keys())

    usuario = st.selectbox("Usuário", [""] + usuarios, key="login_usuario")

    senha = st.text_input("Senha", type="password", key="login_senha")

    if st.button("Entrar"):
        if not setor or not usuario or not senha:
            st.error("Preencha setor, usuário e senha.")
            return

        senha_correta = USUARIOS_POR_SETOR[setor].get(usuario)
        if senha != senha_correta:
            st.error("Senha incorreta.")
            return

        st.session_state.setor_usuario = setor
        st.session_state.usuario_logado = usuario
        st.rerun()


# Gate do app
if not st.session_state.usuario_logado:
    tela_login()
    st.stop()

# Top bar
st.caption(
    f"Logado como **{st.session_state.usuario_logado}** "
    f"({st.session_state.setor_usuario})"
)

if st.button("Trocar usuário"):
    st.session_state.usuario_logado = None
    st.session_state.setor_usuario = None
    st.rerun()

# ======================
# APP PRINCIPAL
# ======================

st.title("Fila de Pedidos")
st.divider()

# Carregar pedidos
pedidos = listar_pedidos()
estados = ESTADOS_DB

# Bloco: Criar pedido (somente se permitido)
if PERMISSOES_POR_TIPO[st.session_state.setor_usuario]["CRIAR"]:
    with st.expander("Criar pedido", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        numero = col1.text_input("Número")
        nome = col2.text_input("Nome/Cliente")
        estado = col3.selectbox("Estado", ESTADOS_DB)
        status = col4.selectbox("Status", STATUS_DB)

        if st.button("Criar"):
            if not numero or not nome:
                st.warning("Preencha número e nome.")
            else:
                criar_pedido(numero, nome, estado, status, st.session_state.usuario_logado)
                st.success("Criado.")
                st.rerun()
else:
    st.info("Somente VENDAS pode criar pedidos.")

st.divider()

# Kanban com permissões por setor
tipo = st.session_state.setor_usuario
move_map = PERMISSOES_POR_TIPO[tipo]["MOVE"]

cols = st.columns(len(estados))

for i, est in enumerate(estados):
    with cols[i]:
        st.subheader(ESTADO_LABEL[est])

        pedidos_do_estado = [x for x in pedidos if x.get("estado_atual") == est]
        for p in pedidos_do_estado:
            st.caption(f'{p.get("numero_pedido")} • {p.get("status")}')
            st.write(p.get("nome_pedido"))

            destinos = move_map.get(est, [])

            # Só mostra botões para destinos permitidos
            for destino in destinos:
                if st.button(
                    f"Mover → {ESTADO_LABEL[destino]}",
                    key=f'{p["id"]}-{destino}'
                ):
                    mover_pedido(
                        p["id"],
                        est,
                        destino,
                        st.session_state.usuario_logado
                    )
                    st.rerun()

            st.divider()
