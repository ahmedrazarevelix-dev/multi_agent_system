// frontend/src/pages/Plans.jsx
import React, { useState, useEffect } from "react";
import { RefreshCw } from "lucide-react";
import { getAllPlans, getPlanById } from "../services/api";
import { Card, PageHeader, PageWrap, StatusBadge, Btn, ResultBox } from "../components/UI";
 
export default function Plans() {
  const [plans,    setPlans]    = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading,  setLoading]  = useState(false);
 
  const load = async () => {
    setLoading(true);
    try { 
      const data = await getAllPlans();
      setPlans(Array.isArray(data) ? data : data.plans || []);
    } catch {} finally { setLoading(false); }
};
 
  useEffect(() => { load(); }, []);
 
  return (
    <PageWrap>
      <PageHeader title="Execution Plans" subtitle="Master Orchestrator ke sare plans aur unka status">
        <Btn onClick={load} loading={loading} variant="secondary" style={{ background: "#1e2a45", color: "#94a3b8" }}>
          <RefreshCw size={14} /> Refresh
        </Btn>
      </PageHeader>
 
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <Card>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 14, textTransform: "uppercase" }}>
            All Plans ({plans.length})
          </div>
          {plans.length === 0
            ? <div style={{ fontSize: 13, color: "#475569" }}>Koi plan nahi abhi tak.</div>
            : plans.slice().reverse().map(p => (
                <div key={p.plan_id} onClick={() => setSelected(p)}
                  style={{ padding: "12px 14px", borderRadius: 8, marginBottom: 8, background: selected?.plan_id === p.plan_id ? "#1e2a45" : "#0f1117", cursor: "pointer" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>{p.plan_id}</span>
                    <StatusBadge status={p.approval_status} />
                  </div>
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{p.classification} · {p.agents_planned} agents</div>
                  <div style={{ fontSize: 11, color: "#475569", marginTop: 2 }}>{p.request?.substring(0,60)}...</div>
                </div>
              ))
          }
        </Card>
 
        <div>
          {selected ? (
            <Card>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#f1f5f9", marginBottom: 14 }}>{selected.plan_id}</div>
              {[
                ["Classification", selected.classification],
                ["Confidence",     selected.confidence + "%"],
                ["Status",         <StatusBadge status={selected.approval_status} />],
                ["Created",        selected.created_at?.substring(0,19)],
                ["Approved",       selected.approved_at?.substring(0,19) || "—"],
                ["Completed",      selected.completed_at?.substring(0,19) || "—"],
              ].map(([label, value]) => (
                <div key={label} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #1e2a45" }}>
                  <span style={{ fontSize: 12, color: "#64748b" }}>{label}</span>
                  <span style={{ fontSize: 12, color: "#94a3b8" }}>{value}</span>
                </div>
              ))}
              <div style={{ marginTop: 14 }}>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>AI APPROVAL REASON</div>
                <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6, background: "#0f1117", borderRadius: 8, padding: "10px 12px" }}>
                  {selected.approval_reason || "—"}
                </div>
              </div>
              <ResultBox result={selected.result} title="Result" />
            </Card>
          ) : (
            <Card style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 200 }}>
              <div style={{ fontSize: 13, color: "#475569" }}>Plan select karein details dekhne ke liye</div>
            </Card>
          )}
        </div>
      </div>
    </PageWrap>
  );
}