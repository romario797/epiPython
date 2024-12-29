import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import json
from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
import os

# Caminho do arquivo JSON para persistência das solicitações
SOLICITACOES_FILE = "solicitacoes.json"

# Função para carregar solicitações salvas
def carregar_solicitacoes():
    if os.path.exists(SOLICITACOES_FILE):
        with open(SOLICITACOES_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return []

# Função para salvar solicitações
def salvar_solicitacoes(solicitacoes):
    with open(SOLICITACOES_FILE, "w", encoding="utf-8") as file:
        json.dump(solicitacoes, file, indent=4, ensure_ascii=False)

# Carregar os dados do motorista.json
with open("motorista.json", "r", encoding="utf-8") as file:
    motoristas = json.load(file)

# Carregar os dados do epis.json
with open("epis.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Carregar solicitações persistidas
if "solicitacoes" not in st.session_state:
    st.session_state["solicitacoes"] = carregar_solicitacoes()

# Função para buscar motorista pelo número de matrícula
def buscar_motorista_por_matricula(matricula):
    for motorista in motoristas:
        if motorista["Matrícula"] == float(matricula):
            return motorista
    return None

# Obter os tipos únicos da lista
tipos = list(set(item["TIPO"] for item in data))

# Navegação no sidebar
menu = st.sidebar.selectbox("Selecione a área", ["Solicitação de EPIs", "Área Restrita - Supervisor"])

# Área de Solicitação de EPIs
if menu == "Solicitação de EPIs":
    st.title("Solicitação de EPIs/Logística Florestal")

    # Limpar solicitações temporárias ao iniciar
    if "solicitacoes_temp" not in st.session_state:
        st.session_state["solicitacoes_temp"] = []

    st.header("Digite sua Matrícula")

    # Campo para digitar a matrícula
    matricula = st.text_input("Matrícula")

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

                # Adicionar o item à lista de solicitações temporárias
                if st.button("Adicionar ao Resumo"):
                    encontrado = False
                    for solicitacao in st.session_state["solicitacoes_temp"]:
                        if solicitacao["Matrícula"] == matricula:
                            # Atualizar a linha existente
                            solicitacao["Descrição"] += f", {descricao_selecionada}"
                            solicitacao["Tipo"] += f", {tipo_selecionado}"
                            solicitacao["Quantidade"] += f", {quantidade}"
                            solicitacao["Código SAP"] += f", {item_escolhido['COD SAP']}"
                            encontrado = True
                            break

                    if not encontrado:
                        # Adicionar nova linha se não encontrado
                        st.session_state["solicitacoes_temp"].append(
                            {
                                "Nome": nome,
                                "Equipe (BTF)": btf,
                                "Função": funcao,
                                "Frota": frota,
                                "Matrícula": matricula,
                                "Tipo": tipo_selecionado,
                                "Descrição": descricao_selecionada,
                                "Quantidade": str(quantidade),
                                "Código SAP": str(item_escolhido["COD SAP"]),
                            }
                        )
                    st.success(f"{descricao_selecionada} adicionado com sucesso!")

                # Mostrar resumo consolidado das solicitações temporárias
                if len(st.session_state["solicitacoes_temp"]) > 0:
                    st.subheader("Resumo das Solicitações")
                    df = pd.DataFrame(st.session_state["solicitacoes_temp"])
                    st.dataframe(df, use_container_width=True)

                # Botão para salvar e limpar a tela
                if st.button("Finalizar Solicitação"):
                    st.session_state["solicitacoes"].extend(st.session_state["solicitacoes_temp"])
                    salvar_solicitacoes(st.session_state["solicitacoes"])
                    st.session_state["solicitacoes_temp"] = []
                    st.success("Solicitações enviadas com sucesso!")

# Área Restrita para Supervisores
elif menu == "Área Restrita - Supervisor":
    st.title("Área Restrita - Supervisor")

    # Simulação de autenticação simples
    senha = st.text_input("Digite a senha para acessar", type="password")
    if senha == "admin123":
        st.success("Acesso permitido!")

        # Exibição das solicitações na área restrita
        if len(st.session_state["solicitacoes"]) > 0:
            st.subheader("Solicitações Registradas")

            df = pd.DataFrame(st.session_state["solicitacoes"])

            # Adicionar coluna "Excluir" se não existir
            if "Excluir" not in df.columns:
                df["Excluir"] = False

            # Configurar o grid para edição e exclusão
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_column("Excluir", editable=True, checkboxSelection=True)  # Checkbox para exclusão
            gb.configure_default_column(editable=True, wrapText=True)  # Permitir edição e wrap de texto
            gb.configure_grid_options(domLayout="autoHeight")  # Altura automática para o grid
            grid_options = gb.build()

            # Exibir a tabela
            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.MANUAL,
                fit_columns_on_grid_load=True,  # Ajustar colunas automaticamente
                height=400,  # Altura padrão
                theme="streamlit",  # Tema compatível com Streamlit
            )

            # Atualizar o DataFrame com as edições feitas no grid
            df_editado = pd.DataFrame(grid_response["data"])

            # Botão para excluir registros selecionados
            if st.button("Excluir selecionados"):
                df_editado = df_editado[df_editado["Excluir"] == False].drop(columns=["Excluir"])
                st.session_state["solicitacoes"] = df_editado.to_dict("records")
                salvar_solicitacoes(st.session_state["solicitacoes"])
                st.success("Registros excluídos com sucesso!")

            # Botão para exportar as alterações para Excel
            def export_to_excel(dataframe):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    dataframe.to_excel(writer, index=False, sheet_name="Solicitações")
                return output.getvalue()

            excel_data = export_to_excel(df_editado)

            st.download_button(
                label="Baixar Excel Atualizado",
                data=excel_data,
                file_name=f"solicitacoes_atualizadas_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    else:
        if senha:
            st.error("Senha incorreta. Tente novamente.")
