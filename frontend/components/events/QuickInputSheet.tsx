"use client";
import { useState, useEffect } from "react";
import { X, ChevronRight, Copy } from "lucide-react";
import { api, EventCreate } from "@/lib/api";
import { queueEvent, syncOfflineQueue } from "@/lib/offline";

type EventType = "FEEDING" | "MORTALITY" | "SAMPLING" | "TREATMENT" | "ENVIRONMENT" | "NOTE";

const EVENT_LABELS: Record<EventType, string> = {
  FEEDING: "給餌",
  MORTALITY: "死亡",
  SAMPLING: "計測",
  TREATMENT: "投薬",
  ENVIRONMENT: "環境",
  NOTE: "メモ",
};

const EVENT_ICONS: Record<EventType, string> = {
  FEEDING: "🐟",
  MORTALITY: "💀",
  SAMPLING: "📏",
  TREATMENT: "💊",
  ENVIRONMENT: "🌡️",
  NOTE: "📝",
};

interface Props {
  cageId: number;
  cageName: string;
  defaultType?: EventType;
  onClose: () => void;
  onSuccess: () => void;
}

export default function QuickInputSheet({
  cageId,
  cageName,
  defaultType,
  onClose,
  onSuccess,
}: Props) {
  const [step, setStep] = useState<"type" | "form">(defaultType ? "form" : "type");
  const [eventType, setEventType] = useState<EventType>(defaultType || "FEEDING");
  const [payload, setPayload] = useState<Record<string, string | number>>({});
  const [prevPayload, setPrevPayload] = useState<Record<string, unknown> | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // 前回値ロード
  useEffect(() => {
    if (step === "form") {
      api.lastEvent(cageId, eventType)
        .then((ev) => {
          if (ev) setPrevPayload(ev.payload_json);
        })
        .catch(() => {});
    }
  }, [cageId, eventType, step]);

  function copyPrev() {
    if (!prevPayload) return;
    const copy: Record<string, string | number> = {};
    Object.entries(prevPayload).forEach(([k, v]) => {
      if (typeof v === "number" || typeof v === "string") copy[k] = v;
    });
    setPayload(copy);
  }

  function set(key: string, value: string | number) {
    setPayload((p) => ({ ...p, [key]: value }));
  }

  async function submit() {
    setSaving(true);
    setError("");
    const event: EventCreate = {
      event_type: eventType,
      occurred_at: new Date().toISOString(),
      cage_id: cageId,
      payload_json: payload,
    };

    try {
      if (navigator.onLine) {
        await api.createEvent(event);
        // オフラインキューも同期
        syncOfflineQueue(api.syncPush).catch(() => {});
      } else {
        await queueEvent(event);
      }
      onSuccess();
    } catch (e: unknown) {
      // オフライン時はキューへ
      await queueEvent(event);
      onSuccess();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col justify-end">
      {/* Overlay */}
      <div className="absolute inset-0 bottom-sheet-overlay" onClick={onClose} />

      {/* Sheet */}
      <div className="relative bg-white rounded-t-3xl shadow-2xl slide-up">
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-1">
          <div className="w-10 h-1 bg-ocean-200 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-4 pb-3 border-b border-ocean-100">
          <div>
            <h2 className="font-bold text-ocean-900">
              {step === "type" ? "作業を選択" : EVENT_LABELS[eventType]}
            </h2>
            <p className="text-xs text-ocean-400">{cageName}</p>
          </div>
          <button onClick={onClose} className="text-ocean-400 hover:text-ocean-600 p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {step === "type" && (
            <div className="grid grid-cols-3 gap-3">
              {(Object.keys(EVENT_LABELS) as EventType[]).map((t) => (
                <button
                  key={t}
                  onClick={() => {
                    setEventType(t);
                    setPayload({});
                    setPrevPayload(null);
                    setStep("form");
                  }}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl border-2 border-ocean-100 hover:border-ocean-400 hover:bg-ocean-50 transition-colors active:scale-95"
                >
                  <span className="text-3xl">{EVENT_ICONS[t]}</span>
                  <span className="text-sm font-medium text-ocean-800">{EVENT_LABELS[t]}</span>
                </button>
              ))}
            </div>
          )}

          {step === "form" && (
            <div className="space-y-4">
              {/* 前回値コピー */}
              {prevPayload && (
                <button
                  onClick={copyPrev}
                  className="w-full flex items-center gap-2 text-sm text-ocean-600 bg-ocean-50 rounded-xl px-4 py-2 hover:bg-ocean-100"
                >
                  <Copy className="w-4 h-4" />
                  前回値をコピー
                </button>
              )}

              {eventType === "FEEDING" && (
                <FeedingForm payload={payload} set={set} />
              )}
              {eventType === "MORTALITY" && (
                <MortalityForm payload={payload} set={set} />
              )}
              {eventType === "SAMPLING" && (
                <SamplingForm payload={payload} set={set} />
              )}
              {eventType === "TREATMENT" && (
                <TreatmentForm payload={payload} set={set} />
              )}
              {eventType === "ENVIRONMENT" && (
                <EnvironmentForm payload={payload} set={set} />
              )}
              {eventType === "NOTE" && (
                <NoteForm payload={payload} set={set} />
              )}

              {error && (
                <p className="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2">{error}</p>
              )}

              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setStep("type")}
                  className="flex-1 border border-ocean-200 text-ocean-600 font-medium py-3 rounded-xl hover:bg-ocean-50"
                >
                  戻る
                </button>
                <button
                  onClick={submit}
                  disabled={saving}
                  className="flex-2 flex-grow-[2] bg-ocean-600 text-white font-semibold py-3 rounded-xl hover:bg-ocean-700 disabled:opacity-50 transition-colors"
                >
                  {saving ? "保存中..." : "保存"}
                </button>
              </div>
            </div>
          )}
        </div>
        <div className="h-safe-area" />
      </div>
    </div>
  );
}

type FormProps = {
  payload: Record<string, string | number>;
  set: (key: string, value: string | number) => void;
};

function FeedingForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="給餌量 (kg)" required>
        <input
          type="number"
          step="0.1"
          value={payload.feed_kg ?? ""}
          onChange={(e) => set("feed_kg", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 25.5"
        />
      </Field>
      <Field label="餌の種類">
        <select
          value={payload.feed_type ?? ""}
          onChange={(e) => set("feed_type", e.target.value)}
          className="form-input"
        >
          <option value="">選択してください</option>
          <option value="生餌">生餌</option>
          <option value="配合飼料">配合飼料</option>
          <option value="EP">EP</option>
        </select>
      </Field>
      <Field label="メモ">
        <input
          type="text"
          value={payload.memo ?? ""}
          onChange={(e) => set("memo", e.target.value)}
          className="form-input"
          placeholder="特記事項があれば"
        />
      </Field>
    </div>
  );
}

function MortalityForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="死亡尾数" required>
        <input
          type="number"
          value={payload.dead_count ?? ""}
          onChange={(e) => set("dead_count", parseInt(e.target.value))}
          className="form-input"
          placeholder="例: 5"
        />
      </Field>
      <Field label="原因（推定）">
        <select
          value={payload.cause_guess ?? ""}
          onChange={(e) => set("cause_guess", e.target.value)}
          className="form-input"
        >
          <option value="">不明</option>
          <option value="病気">病気</option>
          <option value="傷害">傷害</option>
          <option value="酸欠">酸欠</option>
          <option value="水温">水温異常</option>
          <option value="その他">その他</option>
        </select>
      </Field>
      <Field label="メモ">
        <input
          type="text"
          value={payload.memo ?? ""}
          onChange={(e) => set("memo", e.target.value)}
          className="form-input"
          placeholder="状況詳細"
        />
      </Field>
    </div>
  );
}

function SamplingForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="サンプル数" required>
        <input
          type="number"
          value={payload.sample_count ?? ""}
          onChange={(e) => set("sample_count", parseInt(e.target.value))}
          className="form-input"
          placeholder="例: 20"
        />
      </Field>
      <Field label="平均体重 (g)" required>
        <input
          type="number"
          step="0.1"
          value={payload.avg_weight_g ?? ""}
          onChange={(e) => set("avg_weight_g", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 620.5"
        />
      </Field>
      <Field label="平均体長 (cm)">
        <input
          type="number"
          step="0.1"
          value={payload.avg_length_cm ?? ""}
          onChange={(e) => set("avg_length_cm", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 35.2"
        />
      </Field>
    </div>
  );
}

function TreatmentForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="薬品名" required>
        <input
          type="text"
          value={payload.drug_name ?? ""}
          onChange={(e) => set("drug_name", e.target.value)}
          className="form-input"
          placeholder="薬品名"
        />
      </Field>
      <Field label="投与量" required>
        <input
          type="number"
          step="0.01"
          value={payload.dose ?? ""}
          onChange={(e) => set("dose", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 1.5"
        />
      </Field>
      <Field label="単位">
        <select
          value={payload.unit ?? ""}
          onChange={(e) => set("unit", e.target.value)}
          className="form-input"
        >
          <option value="ml">ml</option>
          <option value="g">g</option>
          <option value="mg">mg</option>
          <option value="kg">kg</option>
        </select>
      </Field>
      <Field label="理由">
        <input
          type="text"
          value={payload.reason ?? ""}
          onChange={(e) => set("reason", e.target.value)}
          className="form-input"
          placeholder="投薬理由"
        />
      </Field>
    </div>
  );
}

function EnvironmentForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="水温 (℃)" required>
        <input
          type="number"
          step="0.1"
          value={payload.water_temp_c ?? ""}
          onChange={(e) => set("water_temp_c", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 18.5"
        />
      </Field>
      <Field label="溶存酸素 (mg/L)">
        <input
          type="number"
          step="0.1"
          value={payload.do_mg_l ?? ""}
          onChange={(e) => set("do_mg_l", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 7.2"
        />
      </Field>
      <Field label="塩分 (PSU)">
        <input
          type="number"
          step="0.1"
          value={payload.salinity_psu ?? ""}
          onChange={(e) => set("salinity_psu", parseFloat(e.target.value))}
          className="form-input"
          placeholder="例: 33.5"
        />
      </Field>
      <Field label="メモ">
        <input
          type="text"
          value={payload.memo ?? ""}
          onChange={(e) => set("memo", e.target.value)}
          className="form-input"
          placeholder="潮流など"
        />
      </Field>
    </div>
  );
}

function NoteForm({ payload, set }: FormProps) {
  return (
    <div className="space-y-3">
      <Field label="メモ内容" required>
        <textarea
          value={payload.content ?? ""}
          onChange={(e) => set("content", e.target.value)}
          className="form-input min-h-[100px] resize-none"
          placeholder="自由記述"
        />
      </Field>
    </div>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-ocean-800 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </label>
      {children}
    </div>
  );
}
