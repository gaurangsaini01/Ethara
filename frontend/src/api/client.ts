import axios from "axios";

const baseURL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

export const api = axios.create({ baseURL });

export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    // FastAPI request-validation errors arrive as a list of { loc, msg, ... }.
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: { msg?: string }) => d.msg ?? "Invalid input").join(", ");
    }
    return error.message;
  }
  return "Something went wrong. Please try again.";
}
