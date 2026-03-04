"use client";
import { Event } from "@/lib/api";

const EVENT_LABELS: Record<string, string> = {
  FEEDING: "給餌",
  MORTALITY: "死亡",
  SAMPLING: "計測",
  TREATMENT: "投薬",
  ENVIRONMENT: "環境",
  MOVE: "移動",
  SPLIT: "分養",
  MERGE: "統合",
  HARVEST: "出荷",
  NOTE: "メモ",
};

const EVENT_ICONS: Record<string, string> = {
  FEEDING: "🐟",
  MORTALITY: "💀",
  SAMPLING: "📏",
  TREATMENT: "💊",
  ENVIRONMENT: "🌡️",
  MOVE: "🔄",
  SPLIT: "✂️",
  MERGE: "🔗",
  HARVEST: "📦",
  NOTE: "📝",
};

function formatPayload(type: string, payload: Record<string, unknown>): string {
  switch (type) {
    case "FEEDING":
      return `${payload.feed_kg}kg${payload.feed_type ? ` (${payload.feed_type})` : ""}`;
    case "MORTALITY":
      return `${payload.dead_count}尾${payload.cause_guess ? ` / ${payload.cause_guess}` : ""}`;
    case "SAMPLING":
      return `${payload.sample_count}尾 平均${payload.avg_weight_g}g`;
    case "TREATMENT":
      return `${payload.drug_name} ${payload.dose}${payload.unit}`;
    case "ENVIRONMENT":
      return `水温${payload.water_temp_c}℃${payload.do_mg_l ? ` DO:${payload.do_mg_l}` : ""}`;
    case "NOTE":
      return String(payload.content || "");
    default:
      return JSON.stringify(payload);
  }
}

function formatDateTime(iso: string): string {
  const d = new Date(iso);
  const date = `${d.getMonth() + 1}/${d.getDate()}`;
  const time = `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
  return `${date} ${time}`;
}

export default function EventList({ events }: { events: Event[] }) {
  if (events.length === 0) {
    return <p className="text-center text-ocean-300 py-6">記録なし</p>;
  }

  return (
    <div className="space-y-2">
      {events.map((ev) => (
        <div key={ev.id} className="card-ocean px-4 py-3 flex items-start gap-3">
          <span className="text-xl mt-0.5">{EVENT_ICONS[ev.event_type] || "📋"}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-ocean-800">
                {EVENT_LABELS[ev.event_type] || ev.event_type}
              </span>
              <span className="text-xs text-ocean-400">{formatDateTime(ev.occurred_at)}</span>
            </div>
            <p className="text-xs text-ocean-600 mt-0.5 truncate">
              {formatPayload(ev.event_type, ev.payload_json)}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
