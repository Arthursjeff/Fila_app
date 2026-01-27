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


if "ui" not in st.session_state:
    st.session_state.ui = {
        "pedido_aberto": None
    }


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

# ======================
# BLOCO 4.1 — LAYOUT KANBAN BASE
# ======================

# Estados visuais (ordem importa)
ESTADOS_VISUAIS = [
    "PEDIDO",
    "EM_MONTAGEM",
    "PROGRAMADOS_IMPORTACAO",
    "MONTADOS",
    "FATURADO",
    "EMBALADO",
    "RETIRADO",
]


COR_POR_ESTADO = {
    "PEDIDO": "#FFA500",
    "EM_MONTAGEM": "#FFF8B5",
    "PROGRAMADOS_IMPORTACAO": "#C4B5FD",
    "MONTADOS": "#90EE90",
    "FATURADO": "#87CEFA",
    "EMBALADO": "#D8B4FE",
    "RETIRADO": "#A9A9A9",
}


def _hora_curta(p):
    return (
        p.get("ultimo_mov_hora")
        or p.get("ultima_hora")
        or ""
    )

def _usuario_curto(p):
    return (
        p.get("ultimo_mov_usuario")
        or p.get("ultimo_usuario")
        or ""
    )

def _label_compacto(p):
    return f"{p['numero_pedido']} - {p['nome_pedido']} — {_hora_curta(p)} — {_usuario_curto(p)}"


def toggle_pedido(pedido_id):
    atual = st.session_state.ui.get("pedido_aberto")
    st.session_state.ui["pedido_aberto"] = None if atual == pedido_id else pedido_id



def render_setor_base(estado, container):
    pedidos_setor = [
        p for p in pedidos
        if p["estado_atual"] == estado and p.get("status", "ATIVO") == "ATIVO"
    ]

    with container:
        # ======================
        # TÍTULO + CONTADOR
        # ======================
        st.markdown(
            f"### {ESTADO_LABEL[estado]} ({len(pedidos_setor)})"
        )

        # ======================
        # BARRA COLORIDA
        # ======================
        st.markdown(
            f"""
            <div style="
                height: 12px;
                background: {COR_POR_ESTADO[estado]};
                border-radius: 999px;
                margin: 6px 0 14px 0;
            "></div>
            """,
            unsafe_allow_html=True
        )

        # ======================
        # CARTÕES DO SETOR
        # ======================
        for p in pedidos_setor:
            aberto = st.session_state.ui.get("pedido_aberto") == p["id"]

            # ===== CARTÃO FECHADO =====
            if not aberto:
                if st.button(
                    _label_compacto(p),
                    key=f"open-{p['id']}",
                    use_container_width=True,
                ):
                    toggle_pedido(p["id"])
                    st.rerun()

            # ===== CARTÃO ABERTO =====
            else:
                with st.container(border=True):
                    st.markdown(
                        f"### {p['numero_pedido']} - {p['nome_pedido']}"
                    )

                    # Última movimentação
                    if p.get("ultimo_mov_hora"):
                        st.caption(
                            f"Última movimentação: "
                            f"{p.get('ultimo_mov_hora')} • "
                            f"{p.get('ultimo_mov_usuario')}"
                        )

                    st.divider()

                    # Histórico (últimos 5 eventos)
                    if p.get("historico"):
                        st.markdown("**Histórico:**")
                        for h in p["historico"][-5:][::-1]:
                            st.write(f"• {h}")
                    else:
                        st.caption("Sem histórico.")

                    st.divider()

                    # Botões (placeholder — regras entram no próximo bloco)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.button("⬅️ Voltar", disabled=True)
                    with c2:
                        st.button("➡️ Avançar", disabled=True)

                    st.divider()

                    if st.button(
                        "⬆️ Fechar",
                        key=f"close-{p['id']}"
                    ):
                        toggle_pedido(p["id"])
                        st.rerun()



# ======================
# RENDERIZAÇÃO 3 × 3
# ======================

linha1 = st.columns(3)
linha2 = st.columns(3)
linha3 = st.columns(1)

for i, estado in enumerate(ESTADOS_VISUAIS[:3]):
    render_setor_base(estado, linha1[i])

for i, estado in enumerate(ESTADOS_VISUAIS[3:6]):
    render_setor_base(estado, linha2[i])

render_setor_base(ESTADOS_VISUAIS[6], linha3[0])


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
