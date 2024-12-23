import streamlit as st
import json
from io import BytesIO
import pandas as pd

# Carregar os dados do motorista.json (nova base)
with open("motorista.json", "r", encoding="utf-8") as file:
    motoristas = json.load(file)

# Carregar os dados do epis.json
with open("epis.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Função para buscar motorista pelo número de matrícula
def buscar_motorista_por_matricula(matricula):
    for motorista in motoristas:
        if motorista["Matrícula"] == float(matricula):
            return motorista
    return None

# Obter os tipos únicos da lista
tipos = list(set(item["TIPO"] for item in data))

# Interface no Streamlit
st.title("Solicitação de EPIs/Logística Florestal")
st.header("Digite sua Matrícula")

# Campo para digitar a matrícula
matricula = st.text_input("Matrícula")

# Busca no motorista.json
motorista = None
if matricula:
    motorista = buscar_motorista_por_matricula(matricula)

if motorista:
    nome = motorista["Nome"]
    btf = motorista["Equipe"]
    funcao = motorista["Função"]
    frota = motorista["Frota"]

    st.success("Matrícula encontrada!")
    st.write(f"**Nome:** {nome}")
    st.write(f"**Equipe (BTF):** {btf}")
    st.write(f"**Função:** {funcao}")
    st.write(f"**Frota:** {frota}")

    st.header("Selecione os EPIs necessários")

    # Passo 1: Selecionar o tipo de EPI
    tipo_selecionado = st.selectbox("Escolha o tipo de EPI", ["Selecione"] + tipos)

    if tipo_selecionado != "Selecione":
        # Filtrar os itens disponíveis para o tipo selecionado
        itens = [item for item in data if item["TIPO"] == tipo_selecionado]

        # Passo 2: Selecionar o item específico
        descricao_selecionada = st.selectbox(
            "Escolha o EPI", ["Selecione"] + [item["DESCRIÇÃO"] for item in itens]
        )

        if descricao_selecionada != "Selecione":
            # Obter o item selecionado
            item_escolhido = next(
                item for item in itens if item["DESCRIÇÃO"] == descricao_selecionada
            )

            # Exibir o limite de quantidade
            max_qtd = item_escolhido["quantidades permitidas"]
            quantidade = st.number_input(
                f"Quantidade (Máximo: {max_qtd})", min_value=0, max_value=max_qtd, step=1
            )

            # Adicionar o item à lista de solicitações
            if st.button("Adicionar ao Resumo"):
                if "solicitacoes" not in st.session_state:
                    st.session_state["solicitacoes"] = []
                st.session_state["solicitacoes"].append(
                    {
                        "Nome": nome,
                        "Equipe (BTF)": btf,
                        "Função": funcao,
                        "Frota": frota,
                        "Matrícula": matricula,
                        "Tipo": tipo_selecionado,
                        "Descrição": descricao_selecionada,
                        "Quantidade": quantidade,
                        "Código SAP": item_escolhido["COD SAP"],
                    }
                )
                st.success(f"{descricao_selecionada} adicionado com sucesso!")

    # Mostrar resumo das solicitações
    if "solicitacoes" in st.session_state and st.session_state["solicitacoes"]:
        st.subheader("Resumo das Solicitações")

        # Criar um DataFrame para exibir como tabela
        df = pd.DataFrame(st.session_state["solicitacoes"])
        st.dataframe(df)

        # Função para converter DataFrame em Excel
        @st.cache_data
        def convert_df_to_excel(dataframe):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                dataframe.to_excel(writer, index=False, sheet_name="Solicitações")
            processed_data = output.getvalue()
            return processed_data

        # Gerar o arquivo Excel
        excel_data = convert_df_to_excel(df)

        # Botão para download do Excel
        st.download_button(
            label="Baixar como Excel",
            data=excel_data,
            file_name="solicitacoes_epis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        if st.button("Finalizar Solicitação"):
            st.success("Solicitação finalizada com sucesso!")
            st.session_state["solicitacoes"] = []  # Limpar resumo após finalizar
else:
    if matricula:
        st.error("Matrícula não encontrada. Por favor, verifique e tente novamente.")
