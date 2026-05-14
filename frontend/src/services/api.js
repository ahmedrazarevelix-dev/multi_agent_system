import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
  timeout: 120000,
  headers: { "Content-Type": "application/json" },
});

API.interceptors.request.use((config) => {
  console.log(`API → ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

API.interceptors.response.use(
  (res) => res.data,
  (err) => {
    const msg = err.response?.data?.detail || err.message || "Unknown error";
    console.error("API Error:", msg);
    return Promise.reject(new Error(msg));
  }
);

export const getSystemInfo      = () => API.get("/");
export const getHealthCheck     = () => API.get("/health");
export const getAllPlans        = () => API.get("/plans");
export const getPlanById        = (id) => API.get(`/plans/${id}`);
export const orchestrate        = (request, context) => API.post("/orchestrate", { request, context });
export const triggerDailyScan   = () => API.post("/agents/daily-scan");
export const runCustomerService = (customer_id, complaint) => API.post("/agents/customer-service", { customer_id, complaint });
export const runInventoryCheck  = () => API.post("/agents/inventory");
export const runFinanceCheck    = () => API.post("/agents/finance");
export const runOperationsCheck = () => API.post("/agents/operations");