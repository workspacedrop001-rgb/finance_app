import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Finance App CNC", layout="wide")

# --- Dados iniciais ---
if "movs" not in st.session_state:
    st.session_state.movs = pd.DataFrame(columns=["tipo","descricao","categoria","valor","data","observacoes","pessoaProlabore"])

if "reserva" not in st.session_state:
    st.session_state.reserva = 2000

# --- Funções ---
def moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def add_movimento(tipo, descricao, categoria, valor, data, obs, pessoa):
    st.session_state.movs.loc[len(st.session_state.movs)] = [tipo, descricao, categoria, valor, data, obs, pessoa]
    st.success("Movimento adicionado!")

def exportar_pdf(df):
    # Exporta resumo para PDF simples (via HTML)
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório Financeiro CNC", ln=True, align='C')
    pdf.ln(10)
    for i, row in df.iterrows():
        pdf.cell(0, 8, txt=f"{row['data']} - {row['tipo']} - {row['descricao']} - {moeda(row['valor'])}", ln=True)
    pdf_output = BytesIO()
    pdf.output(pdf_output)
    return pdf_output

# --- Menu ---
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Movimentações", "Relatórios", "Configurações"])

# --- Dashboard ---
if menu == "Dashboard":
    receita_total = st.session_state.movs[st.session_state.movs.tipo=="Receita"]["valor"].sum()
    despesas_totais = st.session_state.movs[st.session_state.movs.tipo=="Despesa"]["valor"].sum()
    lucro_liquido = receita_total - despesas_totais
    prolabore_lucas = lucro_liquido * 0.3
    prolabore_binho = lucro_liquido * 0.7
    lucro_divisao = lucro_liquido - st.session_state.reserva

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", moeda(receita_total))
    col2.metric("Despesas Totais", moeda(despesas_totais))
    col3.metric("Prolabore Lucas (30%)", moeda(prolabore_lucas))
    col4.metric("Prolabore Binho (70%)", moeda(prolabore_binho))

    st.write("### Resultados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Lucro Líquido", moeda(lucro_liquido))
    col2.number_input("Reserva (editável)", value=st.session_state.reserva, key="reserva_input", on_change=lambda: st.session_state.update({"reserva": st.session_state.reserva_input}))
    col3.metric("Lucro para Divisão", moeda(lucro_divisao))

    st.write("### Receitas vs Despesas")
    fig, ax = plt.subplots(figsize=(8,4))
    movs_mes = st.session_state.movs.groupby("tipo")["valor"].sum()
    ax.bar(["Receitas"], [movs_mes.get("Receita",0)], color="green")
    ax.bar(["Despesas"], [movs_mes.get("Despesa",0)], color="red")
    st.pyplot(fig)

    st.write("### Distribuição de Despesas")
    desp = st.session_state.movs[st.session_state.movs.tipo=="Despesa"].groupby("categoria")["valor"].sum()
    fig2, ax2 = plt.subplots()
    ax2.pie(desp, labels=desp.index, autopct="%1.1f%%")
    st.pyplot(fig2)

# --- Movimentações ---
elif menu == "Movimentações":
    st.write("## Novo Movimento")
    with st.form("form_mov"):
        tipo = st.selectbox("Tipo*", ["Receita","Despesa"])
        descricao = st.text_input("Descrição*")
        categoria = st.selectbox("Categoria*", ["Vendas","Serviços","Outros"] if tipo=="Receita" else ["Materiais","Abrasivo","Energia","Manutencao","Salarios","Marketing","Prolabore","Outros"])
        pessoa = ""
        if tipo=="Despesa" and categoria=="Prolabore":
            pessoa = st.selectbox("Pessoa (Prolabore)", ["Lucas","Binho"])
        valor = st.number_input("Valor* (R$)", min_value=0.0, step=0.01)
        data = st.date_input("Data*")
        obs = st.text_area("Observações (opcional)")
        submitted = st.form_submit_button("Adicionar Movimento")
        if submitted:
            if not tipo or not descricao or not categoria or not valor or not data:
                st.error("Preencha todos os campos obrigatórios!")
            else:
                add_movimento(tipo, descricao, categoria, valor, data, obs, pessoa)

    st.write("## Lista de Movimentos")
    st.dataframe(st.session_state.movs)

# --- Relatórios ---
elif menu == "Relatórios":
    anos = sorted(st.session_state.movs["data"].dt.year.unique()) if not st.session_state.movs.empty else []
    meses = range(1,13)
    col1, col2, col3 = st.columns(3)
    ano_sel = col1.selectbox("Ano", ["Todos"] + list(anos))
    mes_sel = col2.selectbox("Mês", ["Todos"] + list(meses))
    col3.button("Exportar PDF", on_click=lambda: st.download_button("Download PDF", data=exportar_pdf(st.session_state.movs), file_name="relatorio.pdf"))

    # Filtro
    df_filtrado = st.session_state.movs.copy()
    if ano_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["data"].dt.year==int(ano_sel)]
    if mes_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["data"].dt.month==int(mes_sel)]

    st.dataframe(df_filtrado)

# --- Configurações ---
elif menu == "Configurações":
    st.write("## Configurações do App")
    st.info("Aqui você poderá adicionar configurações futuras.")
