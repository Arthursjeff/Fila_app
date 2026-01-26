import streamlit as st
from supabase import create_client

def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])

def listar_pedidos():
    sb = get_supabase()
    return sb.table("pedidos").select("*").order("criado_em").execute().data

def criar_pedido(numero, nome, estado, status, usuario):
    sb = get_supabase()
    pedido = sb.table("pedidos").insert({
        "numero_pedido": numero,
        "nome_pedido": nome,
        "estado_atual": estado,
        "status": status,
        "criado_por": usuario,
        "ultimo_usuario": usuario,
        "ultima_hora": "now()"
    }).execute().data[0]

    sb.table("pedido_eventos").insert({
        "pedido_id": pedido["id"],
        "tipo_evento": "CRIACAO",
        "descricao": "Pedido criado",
        "autor": usuario
    }).execute()
    return pedido

def mover_pedido(pedido_id, estado_atual, novo_estado, usuario):
    sb = get_supabase()
    res = (
        sb.table("pedidos")
        .update({
            "estado_atual": novo_estado,
            "ultimo_mov_usuario": usuario,
            "ultimo_mov_hora": "now()"
        })
        .eq("id", pedido_id)
        .eq("estado_atual", estado_atual)
        .execute()
    )

    # se não atualizou nada, significa que mudou antes (ou estado errado)
    if not res.data:
        return False

    sb.table("pedido_eventos").insert({
        "pedido_id": pedido_id,
        "tipo_evento": "MOVIMENTACAO",
        "descricao": f"{estado_atual} -> {novo_estado}",
        "autor": usuario
    }).execute()
    return True
