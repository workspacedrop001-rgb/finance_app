import React, { useMemo, useRef, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  BarChart, Bar, PieChart, Pie, Cell, Tooltip, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer
} from "recharts";

const MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
const CATS_RECEITA = ["Vendas","Serviços","Outros"];
const CATS_DESPESA = ["Materiais","Abrasivo","Energia","Manutencao","Salarios","Marketing","Prolabore","Outros"];
const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#AA336A", "#8884d8", "#82ca9d", "#a4de6c"];

function moeda(v:number){
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

export default function FinanceApp() {
  const [activeTab, setActiveTab] = useState<"dashboard"|"movimentacoes"|"relatorios"|"configuracoes">("dashboard");
  const [movs, setMovs] = useState<Array<{id:number,tipo:"Receita"|"Despesa",descricao:string,categoria:string,valor:number,data:string,observacoes?:string,pessoaProlabore?:"Lucas"|"Binho"|""}>>([]);
  const [reserva, setReserva] = useState<number>(2000);

  // Filtros (Relatórios)
  const [filtroAno, setFiltroAno] = useState<string>("");
  const [filtroMes, setFiltroMes] = useState<string>("");

  // ---- Movimentações: formulário ----
  const [form, setForm] = useState({
    tipo: "" as "Receita"|"Despesa"|"",
    descricao: "",
    categoria: "",
    valor: "",
    data: "",
    observacoes: "",
    pessoaProlabore: "" as "Lucas"|"Binho"|"",
  });

  const resetForm = () => setForm({tipo:"",descricao:"",categoria:"",valor:"",data:"",observacoes:"",pessoaProlabore:""});

  const addMov = () => {
    const {tipo, descricao, categoria, valor, data} = form;
    const valorNum = parseFloat(String(valor).replace(",","."));
    if(!tipo || !descricao || !categoria || !valorNum || !data){
      alert("Preencha os campos obrigatórios (*)");
      return;
    }
    const novo = { id: Date.now(), ...form, valor: valorNum } as any;
    if(novo.categoria !== "Prolabore") novo.pessoaProlabore = ""; // só se Prolabore
    setMovs(prev => [...prev, novo]);
    resetForm();
  };

  // ---- Cálculos globais (Dashboard) ----
  const receitaTotal = useMemo(() => movs.filter(m=>m.tipo==="Receita").reduce((a,b)=>a+b.valor,0),[movs]);
  const despesasTotais = useMemo(() => movs.filter(m=>m.tipo==="Despesa").reduce((a,b)=>a+b.valor,0),[movs]);
  const lucroLiquido = useMemo(()=> receitaTotal - despesasTotais,[receitaTotal,despesasTotais]);
  const prolaboreLucas = useMemo(()=> lucroLiquido*0.3,[lucroLiquido]);
  const prolaboreBinho = useMemo(()=> lucroLiquido*0.7,[lucroLiquido]);
  const lucroDivisao = useMemo(()=> lucroLiquido - (reserva||0),[lucroLiquido,reserva]);
  const margem = useMemo(()=> receitaTotal>0 ? (lucroLiquido/receitaTotal)*100 : 0,[receitaTotal,lucroLiquido]);

  // ---- Agregações por mês (para gráficos) ----
  const lastNMonths = (n:number) => {
    const arr:{key:string,label:string,year:number,month:number}[] = [];
    const base = new Date(); base.setDate(1);
    for(let i=n-1;i>=0;i--){
      const d = new Date(base.getFullYear(), base.getMonth()-i, 1);
      const y = d.getFullYear();
      const m = d.getMonth();
      arr.push({key:`${y}-${String(m+1).padStart(2,"0")}`,label:MESES_PT[m],year:y,month:m+1});
    }
    return arr;
  };

  const serieReceitaDespesa = useMemo(()=>{
    const months = lastNMonths(6);
    return months.map(({year,month,label})=>{
      const receita = movs.filter(m=>m.tipo==="Receita" && new Date(m.data).getFullYear()===year && (new Date(m.data).getMonth()+1)===month).reduce((a,b)=>a+b.valor,0);
      const despesa = movs.filter(m=>m.tipo==="Despesa" && new Date(m.data).getFullYear()===year && (new Date(m.data).getMonth()+1)===month).reduce((a,b)=>a+b.valor,0);
      return { mes: label, receita, despesa };
    });
  },[movs]);

  const pieDespesas = useMemo(()=>{
    const mapa: Record<string, number> = {};
    CATS_DESPESA.forEach(c=> mapa[c]=0);
    movs.filter(m=>m.tipo==="Despesa").forEach(m=>{ mapa[m.categoria] = (mapa[m.categoria]||0)+m.valor; });
    return Object.entries(mapa).map(([name,value])=>({ name: name==="Manutencao"?"Manutenção":name, value }));
  },[movs]);

  // ---- Relatórios: aplicar filtros ----
  const movsFiltrados = useMemo(()=>{
    return movs.filter(m=>{
      const d = m.data ? new Date(m.data) : null;
      if(!d) return false;
      const passAno = filtroAno ? d.getFullYear()===Number(filtroAno) : true;
      const passMes = filtroMes ? (d.getMonth()+1)===Number(filtroMes) : true;
      return passAno && passMes;
    });
  },[movs,filtroAno,filtroMes]);

  const kpisRel = useMemo(()=>{
    const r = movsFiltrados.filter(m=>m.tipo==="Receita").reduce((a,b)=>a+b.valor,0);
    const d = movsFiltrados.filter(m=>m.tipo==="Despesa").reduce((a,b)=>a+b.valor,0);
    const ll = r - d;
    const pl = ll*0.3; const pb = ll*0.7;
    const mg = r>0 ? (ll/r)*100 : 0;
    return { r, d, pl, pb, ll, mg };
  },[movsFiltrados]);

  const resumoMensal6 = useMemo(()=>{
    const months = lastNMonths(6);
    return months.map(({label,year,month})=>{
      const r = movs.filter(m=>m.tipo==="Receita" && new Date(m.data).getFullYear()===year && (new Date(m.data).getMonth()+1)===month).reduce((a,b)=>a+b.valor,0);
      const d = movs.filter(m=>m.tipo==="Despesa" && new Date(m.data).getFullYear()===year && (new Date(m.data).getMonth()+1)===month).reduce((a,b)=>a+b.valor,0);
      const l = r - d; const mg = r>0 ? (l/r)*100 : 0;
      return { mes: label, receita: r, despesa: d, lucro: l, margem: mg };
    });
  },[movs]);

  const refRelatorios = useRef<HTMLDivElement|null>(null);
  const exportarPDF = () => {
    const conteudo = refRelatorios.current?.innerHTML || "<h1>Relatório</h1>";
    const w = window.open("", "print");
    if(!w) return;
    w.document.write(`<!doctype html><html><head><meta charset='utf-8'><title>Relatório</title>
      <style>body{font-family:Arial,sans-serif;padding:16px} h1,h2{margin:0 0 8px} table{width:100%;border-collapse:collapse;margin-top:8px} th,td{border:1px solid #ddd;padding:6px;text-align:center}</style>
    </head><body>${conteudo}</body></html>`);
    w.document.close();
    w.focus();
    w.print();
  };

  return (
    <div className="p-6 space-y-6">
      {/* Menu */}
      <div className="flex gap-3">
        <Button variant={activeTab==="dashboard"?"default":"outline"} onClick={()=>setActiveTab("dashboard")}>Dashboard</Button>
        <Button variant={activeTab==="movimentacoes"?"default":"outline"} onClick={()=>setActiveTab("movimentacoes")}>Movimentações</Button>
        <Button variant={activeTab==="relatorios"?"default":"outline"} onClick={()=>setActiveTab("relatorios")}>Relatórios</Button>
        <Button variant={activeTab==="config
