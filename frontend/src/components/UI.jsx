// frontend/src/components/UI.jsx
// Reusable UI components used across all pages
 
import React from "react";
import { Loader2 } from "lucide-react";
 
const C = {
  card:    { background: "#161b2e", border: "1px solid #1e2a45", borderRadius: 12, padding: "20px 24px" },
  primary: { background: "#6366f1", color: "#fff", border: "none", borderRadius: 8, padding: "10px 20px", cursor: "pointer", fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 8 },
  input:   { background: "#0f1117", border: "1px solid #1e2a45", borderRadius: 8, padding: "10px 14px", color: "#e2e8f0", fontSize: 13, width: "100%", outline: "none" },
};
 
export function Card({ children, style = {} }) {
  return <div style={{ ...C.card, ...style }}>{children}</div>;
}
 
export function Btn({ children, onClick, loading, disabled, style = {}, variant = "primary" }) {
  const base = variant === "primary" ? C.primary : { ...C.primary, background: "#1e2a45", color: "#94a3b8" };
  return (
    <button onClick={onClick} disabled={disabled || loading} style={{ ...base, opacity: (disabled || loading) ? 0.6 : 1, ...style }}>
      {loading && <Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} />}
      {children}
    </button>
  );
}
 
export function Input({ value, onChange, placeholder, style = {} }) {
  return <input value={value} onChange={onChange} placeholder={placeholder} style={{ ...C.input, ...style }} />;
}
 
export function Textarea({ value, onChange, placeholder, rows = 4, style = {} }) {
  return <textarea value={value} onChange={onChange} placeholder={placeholder} rows={rows} style={{ ...C.input, resize: "vertical", ...style }} />;
}
 
export function Badge({ label, color = "blue" }) {
  const colors = {
    blue:   { bg: "#1e3a5f", text: "#60a5fa" },
    green:  { bg: "#14532d", text: "#4ade80" },
    red:    { bg: "#450a0a", text: "#f87171" },
    yellow: { bg: "#422006", text: "#fbbf24" },
    purple: { bg: "#2e1065", text: "#a78bfa" },
    gray:   { bg: "#1e2a45", text: "#94a3b8" },
  };
  const c = colors[color] || colors.gray;
  return (
    <span style={{ background: c.bg, color: c.text, fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 20, display: "inline-block" }}>
      {label}
    </span>
  );
}
 
export function StatusBadge({ status }) {
  const map = {
    approved: "green", pending: "yellow", rejected: "red",
    running:  "blue",  done:    "green",  failed:   "red",
  };
  return <Badge label={status?.toUpperCase()} color={map[status] || "gray"} />;
}
 
export function PageHeader({ title, subtitle, children }) {
  return (
    <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28 }}>
      <div>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: "#f1f5f9", margin: 0 }}>{title}</h1>
        {subtitle && <p style={{ fontSize: 13, color: "#64748b", marginTop: 4 }}>{subtitle}</p>}
      </div>
      {children}
    </div>
  );
}
 
export function StatCard({ label, value, icon: Icon, color = "#6366f1", sub }) {
  return (
    <Card>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <span style={{ fontSize: 12, color: "#64748b", fontWeight: 500 }}>{label}</span>
        {Icon && <div style={{ width: 32, height: 32, borderRadius: 8, background: color + "22", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Icon size={16} color={color} />
        </div>}
      </div>
      <div style={{ fontSize: 26, fontWeight: 700, color: "#f1f5f9" }}>{value}</div>
      {sub && <div style={{ fontSize: 12, color: "#64748b", marginTop: 4 }}>{sub}</div>}
    </Card>
  );
}
 
export function ResultBox({ result, title = "Agent Result" }) {
  if (!result) return null;
  return (
    <Card style={{ marginTop: 20 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>{title}</div>
      <pre style={{ fontSize: 12, color: "#94a3b8", whiteSpace: "pre-wrap", wordBreak: "break-word", fontFamily: "monospace", lineHeight: 1.6, maxHeight: 400, overflowY: "auto", margin: 0 }}>
        {typeof result === "object" ? JSON.stringify(result, null, 2) : result}
      </pre>
    </Card>
  );
}
 
export function Spinner() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 12, padding: 40, color: "#64748b" }}>
      <Loader2 size={20} style={{ animation: "spin 1s linear infinite" }} />
      <span style={{ fontSize: 14 }}>Agents kaam kar rahe hain...</span>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
 
export function PageWrap({ children }) {
  return <div style={{ padding: "28px 32px", maxWidth: 1100, margin: "0 auto" }}>{children}</div>;
}