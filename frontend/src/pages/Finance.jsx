// frontend/src/pages/Finance.jsx
import React, { useState } from "react";
import { DollarSign } from "lucide-react";
import toast from "react-hot-toast";
import { runFinanceCheck } from "../services/api";
import { Card, Btn, PageHeader, PageWrap, ResultBox, Spinner } from "../components/UI";
 
export default function Finance() {
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
 
  async function run() {
    setLoading(true); setResult(null);
    try {
      const data = await runFinanceCheck();
      setResult(data); toast.success("Finance + Fraud crew complete!");
    } catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }
 
  return (
    <PageWrap>
      <PageHeader title="Finance & Fraud Detection" subtitle="Financial Analysis Agent + Fraud Detection Agent" />
      <Card style={{ marginBottom: 20 }}>
        <p style={{ fontSize: 13, color: "#94a3b8", marginBottom: 16, lineHeight: 1.7 }}>
          Yeh crew: <strong style={{ color: "#f1f5f9" }}>fraud scan</strong> karega last 24 hours ki transactions pe, suspicious transactions freeze karega, financial report generate karega, aur cash flow analyze karega.
        </p>
        <Btn onClick={run} loading={loading}><DollarSign size={14} /> Run Finance & Fraud Check</Btn>
      </Card>
      {loading && <Card><Spinner /></Card>}
      {result && !loading && <ResultBox result={result} />}
    </PageWrap>
  );
}