// frontend/src/pages/Dashboard.jsx
import React, { useState, useEffect } from "react";
import { Bot, Users, ShoppingCart, DollarSign, Cpu, Activity, CheckCircle, AlertTriangle } from "lucide-react";
import { getSystemInfo, getHealthCheck, getAllPlans } from "../services/api";
import { Card, StatCard, PageHeader, PageWrap, Badge } from "../components/UI";
 
const modules = [
  { name: "Customer Service", agents: "Support + Sentiment",       icon: Users,       color: "#06b6d4", module: "customer_service" },
  { name: "Inventory",        agents: "Inventory + Supply Chain",  icon: ShoppingCart,color: "#8b5cf6", module: "inventory"        },
  { name: "Finance & Fraud",  agents: "Finance + Fraud Detection", icon: DollarSign,  color: "#f59e0b", module: "finance"          },
  { name: "HR",               agents: "Recruitment + Performance", icon: Users,       color: "#ec4899", module: "hr"               },
  { name: "Sales & Marketing",agents: "Sales Lead + Marketing",    icon: Activity,    color: "#22c55e", module: "sales"            },
  { name: "Legal",            agents: "Legal Document",            icon: CheckCircle, color: "#f97316", module: "legal"            },
  { name: "IT Operations",    agents: "IT Ops + Security",         icon: Cpu,         color: "#ef4444", module: "it"               },
];
 
export default function Dashboard() {
  const [info,   setInfo]   = useState(null);
  const [plans,  setPlans]  = useState([]);
  const [health, setHealth] = useState(null);
 
  useEffect(() => {
    getSystemInfo().then(setInfo).catch(() => {});
    getHealthCheck().then(setHealth).catch(() => {});
    getAllPlans().then(data => setPlans(Array.isArray(data) ? data : data.plans || [])).catch(() => {});
}, []); // ← sirf yeh [] add karo end meinSirf }) ko }, []); se replace karo! ✅

  const done     = plans.filter(p => p.approval_status === "done").length;
  const approved = plans.filter(p => p.approval_status === "approved").length;
  const failed   = plans.filter(p => p.approval_status === "failed").length;
 
  return (
    <PageWrap>
      <PageHeader title="System Dashboard" subtitle="Multi-Agent Business System — Real-time Overview" />
 
      {/* Stats Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 28 }}>
        <StatCard label="Total Agents"     value={info?.agents  || 12} icon={Bot}      color="#6366f1" sub="All active" />
        <StatCard label="Modules"          value={info?.modules || 7}  icon={Activity} color="#22c55e" sub="7 departments" />
        <StatCard label="Plans Completed"  value={done}                icon={CheckCircle} color="#22c55e" sub="Successfully done" />
        <StatCard label="Plans Failed"     value={failed}              icon={AlertTriangle} color="#ef4444" sub="Need attention" />
      </div>
 
      {/* Health + LLM */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 28 }}>
        <Card>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 14, textTransform: "uppercase" }}>System Health</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { label: "API Status",  value: health?.status || "checking...", ok: health?.status === "healthy" },
              { label: "LLM Backbone",value: info?.llm || "Groq LLaMA3-70b (Free)", ok: true },
              { label: "Database",    value: info?.database || "PostgreSQL",          ok: true },
            ].map(({ label, value, ok }) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13, color: "#94a3b8" }}>{label}</span>
                <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                  <div style={{ width: 7, height: 7, borderRadius: "50%", background: ok ? "#22c55e" : "#ef4444" }} />
                  <span style={{ fontSize: 12, color: ok ? "#22c55e" : "#ef4444" }}>{value}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
 
        <Card>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 14, textTransform: "uppercase" }}>Recent Plans</div>
          {plans.length === 0
            ? <div style={{ fontSize: 13, color: "#475569" }}>Abhi koi plan nahi. Orchestrator se start karein!</div>
            : plans.slice(-4).reverse().map(p => (
                <div key={p.plan_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <span style={{ fontSize: 12, color: "#94a3b8" }}>{p.plan_id} — {p.classification}</span>
                  <Badge label={p.approval_status?.toUpperCase()} color={p.approval_status === "done" ? "green" : p.approval_status === "failed" ? "red" : "yellow"} />
                </div>
              ))
          }
        </Card>
      </div>
 
      {/* Modules Grid */}
      <Card>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 18, textTransform: "uppercase" }}>All 7 Modules — 12 Agents</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 12 }}>
          {modules.map(({ name, agents, icon: Icon, color }) => (
            <div key={name} style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", background: "#0f1117", borderRadius: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 9, background: color + "22", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <Icon size={18} color={color} />
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>{name}</div>
                <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{agents}</div>
              </div>
              <div style={{ marginLeft: "auto" }}>
                <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e" }} />
              </div>
            </div>
          ))}
        </div>
      </Card>
    </PageWrap>
  );
}