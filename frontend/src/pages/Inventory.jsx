// frontend/src/pages/Inventory.jsx
import React, { useState } from "react";
import { ShoppingCart } from "lucide-react";
import toast from "react-hot-toast";
import { runInventoryCheck } from "../services/api";
import { Card, Btn, PageHeader, PageWrap, ResultBox, Spinner } from "../components/UI";
 
export default function Inventory() {
  const [loading, setLoading] = useState(false);
  const [result,  setResult]  = useState(null);
 
  async function run() {
    setLoading(true); setResult(null);
    try {
      const data = await runInventoryCheck();
      setResult(data); toast.success("Inventory + Supply Chain crew complete!");
    } catch (e) { toast.error(e.message); }
    finally { setLoading(false); }
  }
 
  return (
    <PageWrap>
      <PageHeader title="Inventory & Supply Chain" subtitle="Inventory Management Agent + Supply Chain Optimizer Agent" />
      <Card style={{ marginBottom: 20 }}>
        <p style={{ fontSize: 13, color: "#94a3b8", marginBottom: 16, lineHeight: 1.7 }}>
          Yeh crew automatically: <strong style={{ color: "#f1f5f9" }}>stock levels check karega</strong>, low stock products identify karega, demand predict karega, best supplier choose karega, aur orders automatically place karega.
        </p>
        <Btn onClick={run} loading={loading}><ShoppingCart size={14} /> Run Inventory Check</Btn>
      </Card>
      {loading && <Card><Spinner /></Card>}
      {result && !loading && <ResultBox result={result} />}
    </PageWrap>
  );
}