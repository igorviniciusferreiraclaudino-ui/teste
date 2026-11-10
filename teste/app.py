import os
import urllib.parse
import pandas as pd
import streamlit as st

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Cardápio Digital", layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
</style>
""",
    unsafe_allow_html=True
)

ARQUIVO_CSV = "teste/cardapio.csv"
NUMERO_WHATSAPP = "5581992462103"  # DDD + Número do restaurante

# 2. CARREGAR O CSV
df_produtos = pd.read_csv(ARQUIVO_CSV)

# 3. NAVEGAÇÃO LATERAL
st.sidebar.title("📌 Menu de Navegação")
pagina = st.sidebar.radio(
    "Ir para:", ["🍔 Cardápio (Clientes)", "⚙️ Painel Admin"]
)

# ==============================================================================
# PÁGINA 1: CLIENTES
# ==============================================================================
if pagina == "🍔 Cardápio (Clientes)":
  st.title("🍔 Cardápio Digital")

  # Filtro por Categoria
  categorias = ["Todas"] + list(df_produtos["categoria"].unique())
  cat_escolhida = st.selectbox("Filtrar por Categoria:", categorias)

  if cat_escolhida != "Todas":
    produtos_exibir = df_produtos[df_produtos["categoria"] == cat_escolhida]
  else:
    produtos_exibir = df_produtos

  # Memória do Carrinho
  if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

  col_produtos, col_carrinho = st.columns([2, 1])

  # Lado Esquerdo: Lista de Produtos
  with col_produtos:
    for index, linha in produtos_exibir.iterrows():
      with st.container(border=True):
        st.subheader(linha["nome"])
        st.write(f"**Ingredientes:** {linha['ingredientes']}")
        st.write(f"**Preço:** R$ {linha['preco']:.2f}")

        if pd.notna(linha["imagem"]) and os.path.exists(str(linha["imagem"])):
          st.image(linha["imagem"], width=200)

        if st.button("➕ Adicionar ao Pedido", key=f"btn_{index}"):
          st.session_state.carrinho.append(linha)
          st.toast(f"{linha['nome']} adicionado!", icon="✅")

  # Lado Direito: Carrinho de Compras
  with col_carrinho:
    st.subheader("🛒 Seu Pedido")
    if len(st.session_state.carrinho) == 0:
      st.write("Seu carrinho está vazio.")
    else:
      total = 0
      texto_wa = "📋 *NOVO PEDIDO*\n\n"

      for item in st.session_state.carrinho:
        st.write(f"• **{item['nome']}** - R$ {item['preco']:.2f}")
        total += item["preco"]
        texto_wa += f"• 1x {item['nome']} - R$ {item['preco']:.2f}\n"

      texto_wa += f"\n*Total:* R$ {total:.2f}"

      link_whatsapp = f"https://wa.me/{NUMERO_WHATSAPP}?text={urllib.parse.quote(texto_wa)}"
      st.markdown(f"[📲 **Enviar Pedido no WhatsApp**]({link_whatsapp})")

      if st.button("🗑️ Limpar Carrinho"):
        st.session_state.carrinho = []
        st.rerun()
