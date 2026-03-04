function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("ikesu_token");
}

export function setToken(token: string) {
  localStorage.setItem("ikesu_token", token);
}

export function clearToken() {
  localStorage.removeItem("ikesu_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`/api${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  // Auth
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<{ id: number; name: string; email: string; role: string }>("/auth/me"),

  // Cages
  cages: () => request<Cage[]>("/cages"),
  cage: (id: number) => request<Cage>(`/cages/${id}`),
  createCage: (body: Partial<Cage>) =>
    request<Cage>("/cages", { method: "POST", body: JSON.stringify(body) }),
  patchCage: (id: number, body: Partial<Cage>) =>
    request<Cage>(`/cages/${id}`, { method: "PATCH", body: JSON.stringify(body) }),
  cageQr: (token: string) => request<{ cage_id: number; redirect: string }>(`/qr/${token}`),

  // Lots
  lots: () => request<Lot[]>("/lots"),
  lot: (id: number) => request<Lot>(`/lots/${id}`),
  receiveLot: (body: LotCreate) =>
    request<Lot>("/lots", { method: "POST", body: JSON.stringify(body) }),
  moveLot: (id: number, body: object) =>
    request<{ ok: boolean }>(`/lots/${id}/move`, { method: "POST", body: JSON.stringify(body) }),
  splitLot: (id: number, body: object) =>
    request<{ ok: boolean }>(`/lots/${id}/split`, { method: "POST", body: JSON.stringify(body) }),
  mergeLots: (body: object) =>
    request<{ ok: boolean }>("/lots/merge", { method: "POST", body: JSON.stringify(body) }),

  // Events
  events: (params: Record<string, string | number | undefined>) => {
    const q = new URLSearchParams(
      Object.fromEntries(
        Object.entries(params)
          .filter(([, v]) => v !== undefined)
          .map(([k, v]) => [k, String(v)])
      )
    ).toString();
    return request<Event[]>(`/events${q ? `?${q}` : ""}`);
  },
  createEvent: (body: EventCreate) =>
    request<Event>("/events", { method: "POST", body: JSON.stringify(body) }),
  lastEvent: (cageId: number, eventType: string) =>
    request<Event | null>(`/events/last/${cageId}/${eventType}`),

  // KPI
  kpiSummary: (siteId?: number) =>
    request<SiteSummary[]>(`/kpi/summary${siteId ? `?site_id=${siteId}` : ""}`),
  kpiCage: (id: number) => request<CageKPI>(`/kpi/cage/${id}`),
  todayTodos: () => request<TodayTodoItem[]>("/kpi/today/todos"),

  // Sync
  syncPush: (events: EventCreate[]) =>
    request<{ created_ids: number[]; errors: string[] }>("/sync/push", {
      method: "POST",
      body: JSON.stringify({ events }),
    }),
};

// Types
export interface Cage {
  id: number;
  site_id: number;
  name: string;
  code: string;
  lat?: number;
  lng?: number;
  size_x?: number;
  size_y?: number;
  depth?: number;
  qr_token: string;
  is_active: boolean;
  created_at: string;
}

export interface Lot {
  id: number;
  species: string;
  stage: string;
  item_label: string;
  origin_type: string;
  received_date: string;
  initial_count: number;
  initial_avg_weight_g: number;
  notes?: string;
  is_active: boolean;
}

export interface LotCreate {
  species: string;
  stage: string;
  item_label: string;
  origin_type: string;
  received_date: string;
  initial_count: number;
  initial_avg_weight_g: number;
  cage_id: number;
  notes?: string;
}

export interface Event {
  id: number;
  event_type: string;
  occurred_at: string;
  cage_id?: number;
  lot_id?: number;
  user_id: number;
  payload_json: Record<string, unknown>;
  created_at: string;
}

export interface EventCreate {
  event_type: string;
  occurred_at: string;
  cage_id?: number;
  lot_id?: number;
  payload_json: Record<string, unknown>;
}

export interface CageKPI {
  cage_id: number;
  cage_name: string;
  lot_id?: number;
  item_label?: string;
  est_count: number;
  est_avg_weight_g: number;
  est_biomass_kg: number;
  mortality_rate_7d?: number;
  fcr_14d?: number;
  sgr?: number;
  days_to_target?: number;
  target_weight_g: number;
  is_fcr_estimated: boolean;
  data_quality: string;
}

export interface SiteSummary {
  site_id: number;
  site_name: string;
  total_biomass_kg: number;
  total_est_count: number;
  cage_count: number;
  active_lot_count: number;
  cages: CageKPI[];
}

export interface TodayTodoItem {
  cage_id: number;
  cage_name: string;
  item_label?: string;
  missing_types: string[];
  last_feeding_at?: string;
}
