// frontend/src/App.jsx
import React from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import {
  LayoutDashboard, Bot, ShoppingCart, DollarSign,
  Users, Cpu, FileText, Send, ClipboardList
} from "lucide-react";
 
import Dashboard       from "./pages/Dashboard";
import Orchestrator    from "./pages/Orchestrator";
import CustomerService from "./pages/CustomerService";
import Inventory       from "./pages/Inventory";
import Finance         from "./pages/Finance";
import Operations      from "./pages/Operations";
import Plans           from "./pages/Plans";
 
const navItems = [
  { to: "/",            icon: LayoutDashboard, label: "Dashboard"       },
  { to: "/orchestrate", icon: Bot,             label: "Orchestrator"    },
  { to: "/plans",       icon: ClipboardList,   label: "Execution Plans" },
  { to: "/customer",    icon: Users,           label: "Customer"        },
  { to: "/inventory",   icon: ShoppingCart,    label: "Inventory"       },
  { to: "/finance",     icon: DollarSign,      label: "Finance"         },
  { to: "/operations",  icon: Cpu,             label: "Operations"      },
];
 
export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" />
      <div style={{ display: "flex", minHeight: "100vh", background: "#0f1117", color: "#e2e8f0", fontFamily: "Inter, sans-serif" }}>
 
        {/* ── SIDEBAR ── */}
        <aside style={{ width: 220, background: "#161b2e", borderRight: "1px solid #1e2a45", padding: "24px 0", flexShrink: 0 }}>
          {/* Logo */}
          <div style={{ padding: "0 20px 24px", borderBottom: "1px solid #1e2a45" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#6366f1,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Bot size={20} color="#fff" />
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>MultiAgent</div>
                <div style={{ fontSize: 11, color: "#64748b" }}>Business System</div>
              </div>
            </div>
          </div>
 
          {/* Nav */}
          <nav style={{ padding: "16px 12px" }}>
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink key={to} to={to} end={to === "/"} style={({ isActive }) => ({
                display: "flex", alignItems: "center", gap: 10,
                padding: "9px 12px", borderRadius: 8, marginBottom: 4,
                textDecoration: "none", fontSize: 13, fontWeight: 500,
                background: isActive ? "#1e2a45" : "transparent",
                color: isActive ? "#818cf8" : "#94a3b8",
                transition: "all .15s"
              })}>
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </nav>
 
          {/* Status */}
          <div style={{ padding: "16px 20px", borderTop: "1px solid #1e2a45", marginTop: "auto" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e" }} />
              <span style={{ fontSize: 12, color: "#64748b" }}>12 Agents Active</span>
            </div>
            <div style={{ fontSize: 11, color: "#475569", marginTop: 4 }}>Groq LLaMA3 · Free</div>
          </div>
        </aside>
 
        {/* ── MAIN ── */}
        <main style={{ flex: 1, overflow: "auto" }}>
          <Routes>
            <Route path="/"            element={<Dashboard />}       />
            <Route path="/orchestrate" element={<Orchestrator />}    />
            <Route path="/plans"       element={<Plans />}           />
            <Route path="/customer"    element={<CustomerService />} />
            <Route path="/inventory"   element={<Inventory />}       />
            <Route path="/finance"     element={<Finance />}         />
            <Route path="/operations"  element={<Operations />}      />
          </Routes>
        </main>
 
      </div>
    </BrowserRouter>
  );
}