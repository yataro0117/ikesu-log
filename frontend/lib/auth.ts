import { api, setToken, clearToken } from "./api";

export async function login(email: string, password: string): Promise<void> {
  const data = await api.login(email, password);
  setToken(data.access_token);
}

export function logout(): void {
  clearToken();
  window.location.href = "/login";
}

export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("ikesu_token");
}
