"use client";
import { useState } from "react";
import useSWR from "swr";
import { api, Cage, EventCreate } from "@/lib/api";
import { Package, CheckCircle } from "lucide-react";

export default function HarvestPage() {
  const { data: cages } = useSWR("cages", () => api.cages());
  const [selectedCage, setSelectedCage] = useState<number | "">("");
  const [form, setForm] = useState({
    harvest_weight_kg: "",
    harvest_count: "",
    buyer: "",
    price_per_kg: "",
    invoice_no: "",
  });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedCage) {
      setError("生簀を選択してください");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const event: EventCreate = {
        event_type: "HARVEST",
        occurred_at: new Date().toISOString(),
        cage_id: Number(selectedCage),
        payload_json: {
          harvest_weight_kg: parseFloat(form.harvest_weight_kg),
          harvest_count: parseInt(form.harvest_count),
          buyer: form.buyer,
          price_per_kg: form.price_per_kg ? parseFloat(form.price_per_kg) : undefined,
          invoice_no: form.invoice_no || undefined,
        },
      };
      await api.createEvent(event);
      setSuccess(true);
      setForm({ harvest_weight_kg: "", harvest_count: "", buyer: "", price_per_kg: "", invoice_no: "" });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "登録に失敗しました");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-ocean-900 mb-6 flex items-center gap-2">
        <Package className="w-5 h-5 text-ocean-600" />
        出荷登録
      </h1>

      {success && (
        <div className="card-ocean p-4 mb-4 flex items-center gap-3 border-l-4 border-teal-500">
          <CheckCircle className="w-5 h-5 text-teal-500" />
          <p className="text-ocean-800 font-medium">出荷を記録しました</p>
          <button
            onClick={() => setSuccess(false)}
            className="ml-auto text-xs text-ocean-400"
          >
            閉じる
          </button>
        </div>
      )}

      <form onSubmit={submit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-ocean-800 mb-1">
            生簀 <span className="text-red-500">*</span>
          </label>
          <select
            value={selectedCage}
            onChange={(e) => setSelectedCage(e.target.value === "" ? "" : Number(e.target.value))}
            className="form-input"
            required
          >
            <option value="">選択してください</option>
            {cages?.filter((c) => c.is_active).map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-ocean-800 mb-1">
              出荷重量 (kg) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              step="0.1"
              value={form.harvest_weight_kg}
              onChange={(e) => setForm((f) => ({ ...f, harvest_weight_kg: e.target.value }))}
              className="form-input"
              placeholder="例: 2500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ocean-800 mb-1">
              出荷尾数 <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={form.harvest_count}
              onChange={(e) => setForm((f) => ({ ...f, harvest_count: e.target.value }))}
              className="form-input"
              placeholder="例: 500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-ocean-800 mb-1">
            出荷先 <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={form.buyer}
            onChange={(e) => setForm((f) => ({ ...f, buyer: e.target.value }))}
            className="form-input"
            placeholder="例: 〇〇水産"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-ocean-800 mb-1">単価 (円/kg)</label>
            <input
              type="number"
              value={form.price_per_kg}
              onChange={(e) => setForm((f) => ({ ...f, price_per_kg: e.target.value }))}
              className="form-input"
              placeholder="例: 980"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-ocean-800 mb-1">伝票番号</label>
            <input
              type="text"
              value={form.invoice_no}
              onChange={(e) => setForm((f) => ({ ...f, invoice_no: e.target.value }))}
              className="form-input"
              placeholder="例: INV-001"
            />
          </div>
        </div>

        {error && (
          <p className="text-red-600 text-sm bg-red-50 rounded-lg px-3 py-2">{error}</p>
        )}

        <button
          type="submit"
          disabled={saving}
          className="w-full bg-ocean-600 text-white font-semibold py-3 rounded-xl hover:bg-ocean-700 disabled:opacity-50"
        >
          {saving ? "登録中..." : "出荷を記録"}
        </button>
      </form>
    </div>
  );
}
