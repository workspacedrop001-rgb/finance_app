import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ==============================
# CONFIGURAÇÕES INICIAIS
# ==============================
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Data", "Categoria", "Tipo", "Valor"])

if "reserva" not in st.session_state:
    st.session_state.reserva = 0.0

# ==============================
# FUNÇÕES AUXILIARES
# ==============================
def calcular_resultados():
    df = st.session_state.dados
    receitas = df[df["Tipo"] == "Receita"]["Valor"].sum()
    despesas = df[df["Tipo"] == "Despesa"]["Valor"].sum()
    lucro_liquido = receitas - despesas

    # Prolabores (regras fixas)
    prolabore_lucas = lucro_liquido * 0.30
    prolabore_binho = lucro_liquido * 0.70

    # Lucro para divisão (após reserva)
    lucro_para_divisao = lucro_liquido - st.session_state.reserva

    return receitas, despesas, lucro_liquido, prolabore_lucas, prolabore_binho, lucro_para_divisao


# ==============================
# INTERFACE
# ==============================
st.title("💼 Gestão Financeira CNC")

aba = st.sidebar.radio("Navegação", ["Dashboard", "Movimentações", "Relatórios", "Configurações"])

# ==============================
# DASHBOARD
# ==============================
if aba == "Dashboard":
    st.header("📊 Dashboard")

    receitas, despesas, lucro_liquido, prolabore_lucas, prolabore_binho, lucro_para_divisao = calcular_resultados()

    col1, col2, col3 = st.columns(3)
    col1.metric("Receita Total", f"R$ {receitas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Despesas Totais", f"R$ {despesas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("Lucro Líquido", f"R$ {lucro_liquido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    col1, col2, col3 = st.columns(3)
    col1.metric("Prolabore Lucas (30%)", f"R$ {prolabore_lucas:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col2.metric("Prolabore Binho (70%)", f"R$ {prolabore_binho:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    col3.metric("Lucro para Divisão", f"R$ {lucro_para_divisao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # --- Gráfico de Receita vs Despesa ---
    st.subheader("📈 Receitas vs Despesas")
    if not st.session_state.dados.empty:
        df_grouped = st.session_state.dados.groupby("Tipo")["Valor"].sum()
        fig, ax = plt.subplots()
        cores = {"Receita": "green", "Despesa": "red"}
        ax.bar(df_grouped.index, df_grouped.values, color=[cores[t] for t in df_grouped.index])
        ax.set_ylabel("R$ (Reais)")
        st.pyplot(fig)
    else:
        st.info("Ainda não há dados para mostrar.")

    # --- Gráfico Pizza Distribuição ---
    st.subheader("🥧 Distribuição das Despesas")
    df_despesas = st.session_state.dados[st.session_state.dados["Tipo"] == "Despesa"]
    if not df_despesas.empty:
        df_cat = df_despesas.groupby("Categoria")["Valor"].sum()
        fig, ax = plt.subplots()
        ax.pie(df_cat.values, labels=df_cat.index, autopct="%1.1f%%")
        st.pyplot(fig)
    else:
        st.info("Nenhuma despesa registrada ainda.")

# ==============================
# MOVIMENTAÇÕES
# ==============================
elif aba == "Movimentações":
    st.header("📝 Lançamentos")

    with st.form("form_mov"):
        data = st.date_input("Data")
        categoria = st.text_input("Categoria (ex: Materiais, Marketing, etc.)")
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
        enviado = st.form_submit_button("Adicionar")

        if enviado:
            nova_linha = pd.DataFrame([[data, categoria, tipo, valor]], columns=st.session_state.dados.columns)
            st.session_state.dados = pd.concat([st.session_state.dados, nova_linha], ignore_index=True)
            st.success("Movimentação adicionada!")

    st.subheader("📋 Histórico")
    st.dataframe(st.session_state.dados)

# ==============================
# RELATÓRIOS
# ==============================
elif aba == "Relatórios":
    st.header("📑 Relatórios")

    if st.session_state.dados.empty:
        st.info("Nenhum dado disponível.")
    else:
        st.dataframe(st.session_state.dados)

        st.subheader("Resumo por Categoria")
        st.bar_chart(st.session_state.dados.groupby("Categoria")["Valor"].sum())

# ==============================
# CONFIGURAÇÕES
# ==============================
elif aba == "Configurações":
    st.header("⚙️ Configurações")

    reserva = st.number_input("Reserva (R$)", value=float(st.session_state.reserva), step=100.0)
    if st.button("Salvar"):
        st.session_state.reserva = reserva
        st.success("Configurações salvas!")
