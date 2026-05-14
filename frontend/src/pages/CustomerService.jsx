// frontend/src/pages/CustomerService.jsx
import React, { useState } from "react";
import { Send } from "lucide-react";
import toast from "react-hot-toast";
import { runCustomerService } from "../services/api";
import { Card, Btn, Input, Textarea, PageHeader, PageWrap, ResultBox, Spinner } from "../components/UI";
 
export default function CustomerService() {
  const [customerId, setCustomerId] = useState("CUST-001");
  const [complaint,  setComplaint]  = useState("");
  const [loading,    setLoading]    = useState(false);
  const [result,     setResult]     = useState(null);
 
  async function run() {
    if (!complaint.trim()) { toast.error("Complaint likhein!"); return; }
    setLoading(true); setResult(null);
    try {
      const data = await runCustomerService(customerId, complaint);
      setResult(data); toast.success("Customer Service crew complete!");
    } catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }
 
  return (
    <PageWrap>
      <PageHeader title="Customer Service" subtitle="Support Agent + Sentiment Analysis Agent" />
      <Card style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          <div>
            <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 6 }}>Customer ID</label>
            <Input value={customerId} onChange={e => setCustomerId(e.target.value)} placeholder="CUST-001" />
          </div>
          <div>
            <label style={{ fontSize: 12, color: "#64748b", display: "block", marginBottom: 6 }}>Customer Complaint</label>
            <Textarea value={complaint} onChange={e => setComplaint(e.target.value)} placeholder="Customer ki complaint yahan likhein..." rows={4} />
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Btn onClick={run} loading={loading}><Send size={14} /> Run Agents</Btn>
          </div>
        </div>
      </Card>
      {loading && <Card><Spinner /></Card>}
      {result && !loading && <ResultBox result={result} />}
    </PageWrap>
  );
}