// frontend/src/pages/Orchestrator.jsx
import React, { useState } from "react";
import { Send, Zap } from "lucide-react";
import toast from "react-hot-toast";
import { orchestrate, triggerDailyScan } from "../services/api";
import { Card, Btn, Textarea, PageHeader, PageWrap, StatusBadge, Badge, ResultBox, Spinner } from "../components/UI";
 
const QUICK = [
  { label: "Customer Complaint",  text: "Customer CUST-001 is very angry about wrong delivery and wants immediate refund" },
  { label: "Low Stock Alert",     text: "Stock levels are critically low for laptops and USB hubs, need urgent reorder" },
  { label: "Fraud Check",        text: "Suspicious transactions detected today, possible fraud activity needs investigation" },
  { label: "Daily Scan",         text: "Run complete daily scan for all business modules" },
  { label: "HR Review",          text: "Need employee performance report and check underperformers" },
  { label: "IT Security Check",  text: "System health check and security threat scan needed urgently" },
];
 
export default function Orchestrator() {
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
 
  async function submit() {
    if (!request.trim()) { toast.error("Request likhein!"); return; }
    setLoading(true);
    setResult(null);
    try {
      const data = await orchestrate(request);
      setResult(data);
      // Safe check — koi bhi value ho toast dega
      const planId = data?.plan_id || "Done";
      const status = data?.approval_status || data?.status || "success";
      toast.success(`${planId} — ${status}`);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  }
 
  async function dailyScan() {
    setLoading(true);
    try {
      const data = await triggerDailyScan();
      toast.success("Daily scan started!");
      setResult(data);
    } catch (e) {
      toast.error(e.message);
    } finally {
      setLoading(false);
    }
  }
 
  // Backend se jo bhi aaye — safely extract karo
  const classification  = result?.classification  || null;
  const confidence      = result?.confidence      ?? null;
  const agentsPlanned   = result?.agents_planned  ?? null;
  const approvalStatus  = result?.approval_status || result?.status || null;
  const approvalReason  = result?.approval_reason || null;
  const tasks           = result?.tasks           || [];
  const planId          = result?.plan_id         || null;
  const resultText      = result?.result          || (typeof result === "string" ? result : null);
 
  return (
    <PageWrap>
      <PageHeader
        title="Master Orchestrator"
        subtitle="Koi bhi business problem likhein — AI classify, approve, aur solve karega"
      >
        <Btn
          onClick={dailyScan}
          loading={loading}
          variant="secondary"
          style={{ background: "#1e2a45", color: "#94a3b8" }}
        >
          <Zap size={14} /> Daily Scan
        </Btn>
      </PageHeader>
 
      {/* Input card */}
      <Card style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 10, textTransform: "uppercase" }}>
          Business Problem
        </div>
        <Textarea
          value={request}
          onChange={e => setRequest(e.target.value)}
          placeholder="Misal: Customer C001 ka order galat deliver hua, wo bahut angry hai..."
          rows={4}
        />
        <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12 }}>
          <Btn onClick={submit} loading={loading}>
            <Send size={14} /> Orchestrate
          </Btn>
        </div>
      </Card>
 
      {/* Quick examples */}
      <Card style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 12, textTransform: "uppercase" }}>
          Quick Examples
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {QUICK.map(({ label, text }) => (
            <button
              key={label}
              onClick={() => setRequest(text)}
              style={{
                background: "#1e2a45", border: "1px solid #2d3f5e",
                color: "#94a3b8", borderRadius: 8,
                padding: "7px 14px", fontSize: 12, cursor: "pointer"
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </Card>
 
      {/* Loading */}
      {loading && <Card><Spinner /></Card>}
 
      {/* Result */}
      {result && !loading && (
        <div>
          {/* Plan summary card */}
          <Card style={{ marginBottom: 16 }}>
 
            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
              <div style={{ fontSize: 15, fontWeight: 600, color: "#f1f5f9" }}>
                Execution Plan {planId ? `— ${planId}` : ""}
              </div>
              {approvalStatus && <StatusBadge status={approvalStatus} />}
            </div>
 
            {/* Stats row — sirf tab dikhao jab data ho */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 16 }}>
              <div style={{ background: "#0f1117", borderRadius: 8, padding: "10px 14px" }}>
                <div style={{ fontSize: 11, color: "#64748b" }}>Classification</div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "#f1f5f9", marginTop: 4 }}>
                  {classification ? classification.toUpperCase() : "—"}
                </div>
              </div>
              <div style={{ background: "#0f1117", borderRadius: 8, padding: "10px 14px" }}>
                <div style={{ fontSize: 11, color: "#64748b" }}>Confidence</div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "#f1f5f9", marginTop: 4 }}>
                  {confidence !== null ? `${confidence}%` : "—"}
                </div>
              </div>
              <div style={{ background: "#0f1117", borderRadius: 8, padding: "10px 14px" }}>
                <div style={{ fontSize: 11, color: "#64748b" }}>Agents Planned</div>
                <div style={{ fontSize: 15, fontWeight: 600, color: "#f1f5f9", marginTop: 4 }}>
                  {agentsPlanned !== null ? agentsPlanned : "—"}
                </div>
              </div>
            </div>
 
            {/* AI Approval reason */}
            {approvalReason && (
              <div style={{ background: "#0f1117", borderRadius: 8, padding: "12px 14px", marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>AI APPROVAL REASON</div>
                <div style={{ fontSize: 13, color: "#94a3b8", lineHeight: 1.6 }}>{approvalReason}</div>
              </div>
            )}
 
            {/* Tasks list */}
            {tasks.length > 0 && (
              <div>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 10 }}>AGENTS ASSIGNED</div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {tasks.map((t, i) => (
                    <div
                      key={i}
                      style={{
                        display: "flex", alignItems: "center", gap: 10,
                        background: "#0f1117", borderRadius: 8, padding: "10px 14px"
                      }}
                    >
                      <div style={{
                        width: 24, height: 24, borderRadius: "50%",
                        background: "#1e2a45", display: "flex",
                        alignItems: "center", justifyContent: "center",
                        fontSize: 11, color: "#6366f1", fontWeight: 700, flexShrink: 0
                      }}>
                        {i + 1}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>
                          {t.agent || t.agent_name || "Agent"}
                        </div>
                        <div style={{ fontSize: 11, color: "#64748b" }}>
                          {t.description || t.task || ""}
                        </div>
                      </div>
                      {t.priority && (
                        <Badge
                          label={t.priority.toUpperCase()}
                          color={
                            t.priority === "critical" ? "red"
                            : t.priority === "high"   ? "yellow"
                            : "gray"
                          }
                        />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
 
          {/* Result text */}
          {resultText && <ResultBox result={resultText} title="Execution Result" />}
 
          {/* Agar koi structured data na ho — raw JSON dikhao */}
          {!resultText && !classification && (
            <ResultBox result={result} title="Raw Response" />
          )}
        </div>
      )}
    </PageWrap>
  );
}