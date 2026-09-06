// Centralized API configuration
// In development, defaults to local FastAPI server (http://127.0.0.1:8000)
// In production (e.g. Vercel), set VITE_API_BASE_URL in your environment variables.
const rawBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");
