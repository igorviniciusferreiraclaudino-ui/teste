import streamlit as st
import pandas as pd
import os
import urllib.parse

ARQUIVO_CSV = "teste/cardapio.csv"
NUMERO_WHATSAPP = "5581993765676"  # DDD + Número do restaurante

st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
</style>
""",
    unsafe_allow_html=True
)
# 2. CARREGAR O CSV
df_produtos = pd.read_csv(ARQUIVO_CSV)

# 3. NAVEGAÇÃO LATERAL
st.sidebar.title("📌 Menu de Navegação")
pagina = st.sidebar.radio(
    "Ir para:", ["🍔 Cardápio (Clientes)", "⚙️ Painel Admin"]
)
st.title("⚙️ Painel da lanchonete")
SENHA_CORRETA = "admin123"

if "admin_logado" not in st.session_state:
  st.session_state.admin_logado = False

# Tela de Login
if not st.session_state.admin_logado:
  st.subheader("🔒 Acesso Restrito")
  senha_input = st.text_input(
      "Digite a senha do administrador:", type="password"
  )

  if st.button("Entrar"):
    if senha_input == SENHA_CORRETA:
      st.session_state.admin_logado = True
      st.rerun()
    else:
      st.error("Senha incorreta!")

# Área logada do Admin
else:
  col_tit, col_sair = st.columns([3, 1])
  with col_sair:
    if st.button("🚪 Sair"):
      st.session_state.admin_logado = False
      st.rerun()

  # ABAS DO ADMIN: Uma para Cadastrar e outra para Excluir
  aba_cadastrar, aba_excluir = st.tabs(
      ["➕ Cadastrar Produto", "🗑️ Excluir Produto"]
  )

  # ABA 1: FORMULÁRIO DE CADASTRO
  with aba_cadastrar:
    st.subheader("Cadastrar Novo Lanche")
    with st.form("form_cadastrar"):
      nome = st.text_input("Nome do Lanche:")
      categoria = st.text_input("Categoria:")
      ingredientes = st.text_area("Ingredientes / Descrição:")
      preco = st.number_input("Preço (R$):", min_value=0.0, format="%.2f")
      foto = st.file_uploader("Foto do Lanche:", type=["png", "jpg", "jpeg"])

      salvar = st.form_submit_button("Salvar no Cardápio")

      if salvar:
        if not nome or preco <= 0:
          st.error("Preencha o nome e o preço corretamente!")
        else:
          caminho_imagem = ""
          if foto is not None:
            if not os.path.exists("imagens"):
              os.makedirs("imagens")
            caminho_imagem = f"imagens/{foto.name}"
            with open(caminho_imagem, "wb") as f:
              f.write(foto.getbuffer())

          nova_linha = pd.DataFrame([{
              "nome": nome,
              "categoria": categoria,
              "ingredientes": ingredientes,
              "preco": preco,
              "imagem": caminho_imagem,
          }])

          df_produtos = pd.concat(
              [df_produtos, nova_linha], ignore_index=True
          )
          df_produtos.to_csv(ARQUIVO_CSV, index=False)

          st.success(f"'{nome}' cadastrado com sucesso!")
          st.rerun()

  # ABA 2: GERENCIAR E EXCLUIR PRODUTOS
  with aba_excluir:
    st.subheader("Remover Item do Cardápio")

    if df_produtos.empty:
      st.info("Não há produtos cadastrados no CSV para excluir.")
    else:
      # Lista os produtos com o índice numérico
      opcoes_produtos = [
          f"{idx} - {linha['nome']} (R$ {linha['preco']:.2f})"
          for idx, linha in df_produtos.iterrows()
      ]

      item_selecionado = st.selectbox(
          "Escolha o lanche que deseja apagar:", opcoes_produtos
      )

      if st.button("❌ Confirmar Exclusão", type="primary"):
        # Pega a posição (índice) do produto escolhido
        idx_remover = int(item_selecionado.split(" - ")[0])
        nome_removido = df_produtos.loc[idx_remover, "nome"]

        # Remove a linha da tabela no Pandas
        df_produtos = df_produtos.drop(idx_remover)

        # Regrava o arquivo CSV atualizado
        df_produtos.to_csv(ARQUIVO_CSV, index=False)

        st.success(f"Produto '{nome_removido}' removido com sucesso!")
        st.rerun()

  st.markdown("---")
  st.subheader("📋 Lanche Atuais no Cardápio")
  st.dataframe(
      df_produtos[["nome", "categoria", "preco", "ingredientes"]],
      use_container_width=True,
  )