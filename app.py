# finance_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Finance App CNC", layout="wide")

# ===========================
# Dados iniciais
# ===========================
if "movs" not in st.session_state:
    st.session_state.movs = pd.DataFrame(columns=["tipo","descricao","categoria","valor","data","observacoes","pessoaProlabore"])

if "reserva" not in st.session_state:
    st.session_state.reserva = 2000.0

CATS_RECEITA = ["Vendas","Serviços","Outros"]
CATS_DESPESA = ["Materiais","Abrasivo","Energia","Manutenção","Salarios","Marketing","Prolabore","Outros"]

# ===========================
# Funções auxiliares
# ===========================
def moeda(v):
    return f"R${v:,.2f}"

def calcular_kpis(df):
    receita = df[df.tipo=="Receita"]["valor"].sum()
    despesa = df[df.tipo=="Despesa"]["valor"].sum()
    lucro = receita - despesa
    pl = lucro * 0.3
    pb = lucro * 0.7
    margem = (lucro/receita*100) if receita>0 else 0
    lucro_divisao = lucro - st.session_state.reserva
    return receita, despesa, lucro, pl, pb, margem, lucro_divisao

# ===========================
# Menu lateral
# ===========================
st.sidebar.title("Menu")
aba = st.sidebar.radio("Escolha a aba:", ["Dashboard","Movimentações","Relatórios","Configurações"])

# ===========================
# ABA: Dashboard
# ===========================
if aba=="Dashboard":
    st.title("Dashboard Financeiro")
    
    receita, despesa, lucro, pl, pb, margem, lucro_divisao = calcular_kpis(st.session_state.movs)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", moeda(receita))
    col2.metric("Despesas Totais", moeda(despesa))
    col3.metric("Prolabore Lucas", moeda(pl))
    col4.metric("Prolabore Binho", moeda(pb))
    
    st.subheader("Resultados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Lucro Líquido", moeda(lucro))
    col2.number_input("Reserva (editável)", value=st.session_state.reserva, key="reserva_input", step=100.0, on_change=lambda: st.session_state.__setitem__("reserva", st.session_state.reserva_input))
    col3.metric("Lucro para Divisão", moeda(lucro_divisao))
    
    st.subheader("Receitas vs Despesas")
    df_chart = st.session_state.movs.copy()
    if not df_chart.empty:
        df_chart_group = df_chart.groupby([df_chart.data.dt.to_period("M")])["valor","tipo"].sum().unstack(fill_value=0)
        df_chart_group.columns = df_chart_group.columns.droplevel()
        df_chart_group.plot(kind="bar", color=["green","red"])
        st.pyplot(plt.gcf())
        plt.clf()
    
    st.subheader("Distribuição de Despesas")
    df_desp = st.session_state.movs[st.session_state.movs.tipo=="Despesa"]
    if not df_desp.empty:
        df_pie = df_desp.groupby("categoria")["valor"].sum()
        df_pie.plot(kind="pie", autopct="%1.1f%%")
        st.pyplot(plt.gcf())
        plt.clf()

# ===========================
# ABA: Movimentações
# ===========================
elif aba=="Movimentações":
    st.title("Movimentações Financeiras")
    
    with st.form("novo_mov"):
        tipo = st.selectbox("Tipo*", ["","Receita","Despesa"])
        descricao = st.text_input("Descrição*")
        categoria = st.selectbox("Categoria*", CATS_RECEITA if tipo=="Receita" else CATS_DESPESA)
        pessoa = ""
        if categoria=="Prolabore" and tipo=="Despesa":
            pessoa = st.selectbox("Pessoa (Prolabore)", ["Lucas","Binho"])
        valor = st.number_input("Valor* (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data*")
        observacoes = st.text_area("Observações (opcional)")
        submitted = st.form_submit_button("Adicionar Movimento")
        if submitted:
            new_mov = {"tipo":tipo,"descricao":descricao,"categoria":categoria,"valor":valor,"data":pd.to_datetime(data),"observacoes":observacoes,"pessoaProlabore":pessoa}
            st.session_state.movs = pd.concat([st.session_state.movs, pd.DataFrame([new_mov])], ignore_index=True)
            st.success("Movimento adicionado!")

    st.subheader("Lista de Movimentos")
    st.dataframe(st.session_state.movs)

# ===========================
# ABA: Relatórios
# ===========================
elif aba=="Relatórios":
    st.title("Relatórios e Análises")
    st.subheader("Filtros")
    anos = sorted(st.session_state.movs.data.dt.year.unique()) if not st.session_state.movs.empty else []
    meses = list(range(1,13))
    
    col1, col2, col3 = st.columns(3)
    filtro_ano = col1.selectbox("Ano", ["Todos"]+anos)
    filtro_mes = col2.selectbox("Mês", ["Todos"]+meses)
    
    df_rel = st.session_state.movs.copy()
    if filtro_ano!="Todos":
        df_rel = df_rel[df_rel.data.dt.year==filtro_ano]
    if filtro_mes!="Todos":
        df_rel = df_rel[df_rel.data.dt.month==filtro_mes]
    
    receita, despesa, lucro, pl, pb, margem, lucro_divisao = calcular_kpis(df_rel)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Receita Total", moeda(receita))
    col2.metric("Lucro Líquido", moeda(lucro))
    col3.metric("Margem de Lucro", f"{margem:.1f}%")
    col4.metric("Prolabore Lucas", moeda(pl))
    col5.metric("Prolabore Binho", moeda(pb))
    col6.metric("Reserva", moeda(st.session_state.reserva))
    
    st.subheader("Resumo Mensal (últimos 6 meses)")
    if not df_rel.empty:
        resumo = df_rel.copy()
        resumo["mes"] = resumo.data.dt.to_period("M")
        resumo = resumo.groupby("mes")["valor"].agg(["sum"])
        st.dataframe(resumo)
    
    # Exportar PDF simples
    st.subheader("Exportar PDF")
    pdf_buffer = BytesIO()
    st.download_button("Baixar PDF (simples)", data=pdf_buffer.getvalue(), file_name="relatorio.pdf", mime="application/pdf")

# ===========================
# ABA: Configurações
# ===========================
elif aba=="Configurações":
    st.title("Configurações")
    st.info("Aqui você poderá alterar configurações do app no futuro.")
