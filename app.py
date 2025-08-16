import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# Categorias
CATS_RECEITA = ["Vendas","Serviços","Outros"]
CATS_DESPESA = ["Materiais","Abrasivo","Energia","Manutencao","Salarios","Marketing","Prolabore","Outros"]

# Inicializa dados
if "movs" not in st.session_state:
    st.session_state.movs = pd.DataFrame(columns=["tipo","descricao","categoria","valor","data","observacoes","pessoaProlabore"])
if "reserva" not in st.session_state:
    st.session_state.reserva = 2000

# Funções auxiliares
def moeda(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def add_movimento(form):
    valor = float(form["valor"])
    data = form["data"]
    nova = {
        "tipo": form["tipo"],
        "descricao": form["descricao"],
        "categoria": form["categoria"],
        "valor": valor,
        "data": data,
        "observacoes": form.get("observacoes",""),
        "pessoaProlabore": form.get("pessoaProlabore","")
    }
    st.session_state.movs = pd.concat([st.session_state.movs, pd.DataFrame([nova])], ignore_index=True)
    st.success("Movimento adicionado!")

# Menu de abas
abas = ["Dashboard","Movimentações","Relatórios","Configurações"]
aba = st.sidebar.selectbox("Escolha a aba", abas)

# ==================== DASHBOARD ====================
if aba=="Dashboard":
    st.title("Dashboard")
    movs = st.session_state.movs
    receitaTotal = movs[movs.tipo=="Receita"]["valor"].sum()
    despesasTotais = movs[movs.tipo=="Despesa"]["valor"].sum()
    lucroLiquido = receitaTotal - despesasTotais
    prolaboreLucas = lucroLiquido * 0.3
    prolaboreBinho = lucroLiquido * 0.7
    reserva = st.session_state.reserva
    lucroDivisao = lucroLiquido - reserva

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", moeda(receitaTotal))
    col2.metric("Despesas Totais", moeda(despesasTotais))
    col3.metric("Prolabore Lucas (30%)", moeda(prolaboreLucas))
    col4.metric("Prolabore Binho (70%)", moeda(prolaboreBinho))

    st.subheader("Resultados")
    col1, col2, col3 = st.columns(3)
    col1.metric("Lucro Líquido", moeda(lucroLiquido))
    col2.number_input("Reserva (editável)", value=st.session_state.reserva, key="reserva")
    col3.metric("Lucro para Divisão", moeda(lucroDivisao))

    # Gráficos simplificados usando st.bar_chart / st.pyplot se quiser
    st.subheader("Receitas vs Despesas (últimos 6 meses)")
    if not movs.empty:
        movs["data"] = pd.to_datetime(movs["data"])
        ult6 = movs.set_index("data").last("180D").copy()
        resumo = ult6.groupby([pd.Grouper(freq="M"), "tipo"])["valor"].sum().unstack().fillna(0)
        st.bar_chart(resumo)

    st.subheader("Distribuição de Despesas")
    if not movs[movs.tipo=="Despesa"].empty:
        dist = movs[movs.tipo=="Despesa"].groupby("categoria")["valor"].sum()
        st.write(dist)

# ==================== MOVIMENTAÇÕES ====================
elif aba=="Movimentações":
    st.title("Movimentações")
    form = {}
    form["tipo"] = st.selectbox("Tipo*", ["","Receita","Despesa"])
    # Limpa categoria quando tipo muda
    if "last_tipo" not in st.session_state or st.session_state.last_tipo != form["tipo"]:
        form["categoria"] = ""
        st.session_state.last_tipo = form["tipo"]

    if form["tipo"]=="Receita":
        form["categoria"] = st.selectbox("Categoria*", [""] + CATS_RECEITA)
    elif form["tipo"]=="Despesa":
        form["categoria"] = st.selectbox("Categoria*", [""] + CATS_DESPESA)
        if form["categoria"]=="Prolabore":
            form["pessoaProlabore"] = st.selectbox("Pessoa (Prolabore)", ["","Lucas","Binho"])

    form["descricao"] = st.text_input("Descrição*")
    form["valor"] = st.text_input("Valor*")
    form["data"] = st.date_input("Data*", value=datetime.date.today())
    form["observacoes"] = st.text_area("Observações (opcional)")

    if st.button("Adicionar Movimento"):
        if form["tipo"] and form["categoria"] and form["descricao"] and form["valor"]:
            add_movimento(form)
        else:
            st.error("Preencha todos os campos obrigatórios!")

    st.subheader("Lista de Movimentos")
    st.dataframe(st.session_state.movs)

# ==================== RELATÓRIOS ====================
elif aba=="Relatórios":
    st.title("Relatórios e Análises")
    st.write("Acompanhe o desempenho do seu negócio")

    # Filtros
    anos = sorted(st.session_state.movs["data"].dropna().apply(lambda x: x.year).unique()) if not st.session_state.movs.empty else []
    col1, col2, col3 = st.columns(3)
    ano = col1.selectbox("Ano", ["Todos"]+list(anos))
    mes = col2.selectbox("Mês", ["Todos"]]+[str(i) for i in range(1,13)])
    col3.button("Atualizar")

    # Filtra dados
    movs_fil = st.session_state.movs.copy()
    if ano!="Todos":
        movs_fil = movs_fil[movs_fil["data"].dt.year==int(ano)]
    if mes!="Todos":
        movs_fil = movs_fil[movs_fil["data"].dt.month==int(mes)]

    # KPIs
    receita = movs_fil[movs_fil.tipo=="Receita"]["valor"].sum()
    despesa = movs_fil[movs_fil.tipo=="Despesa"]["valor"].sum()
    lucro = receita - despesa
    pl = lucro * 0.3
    pb = lucro * 0.7

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Receita Total", moeda(receita))
    col2.metric("Lucro Líquido", moeda(lucro))
    col3.metric("Prolabore Lucas", moeda(pl))
    col4.metric("Prolabore Binho", moeda(pb))

    # Exportar PDF (simples)
    if st.button("Exportar PDF"):
        st.write("Aqui será implementado PDF")  # Placeholder, depois usamos fpdf ou pdfkit

# ==================== CONFIGURAÇÕES ====================
elif aba=="Configurações":
    st.title("Configurações")
    st.write("Aqui você poderá ajustar configurações futuras do app")
