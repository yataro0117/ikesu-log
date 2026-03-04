"use client";
import useSWR from "swr";
import { api, Cage, CageKPI } from "@/lib/api";
import { useState } from "react";
import { Fish, MapPin, QrCode } from "lucide-react";
import QuickInputSheet from "@/components/events/QuickInputSheet";
import Link from "next/link";

export default function CagesPage() {
  const { data: cages, isLoading } = useSWR("cages", () => api.cages());
  const { data: kpiData } = useSWR("kpi-summary", () => api.kpiSummary());
  const [selected, setSelected] = useState<Cage | null>(null);
  const [view, setView] = useState<"list" | "map">("list");

  const kpiMap = new Map<number, CageKPI>();
  kpiData?.forEach((site) => site.cages.forEach((c) => kpiMap.set(c.cage_id, c)));

  return (
    <div className="p-4 max-w-lg mx-auto">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-xl font-bold text-ocean-900">生簀一覧</h1>
        <div className="flex bg-ocean-100 rounded-xl p-1 gap-1">
          {(["list", "map"] as const).map((v) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                view === v ? "bg-white text-ocean-700 shadow-sm" : "text-ocean-400"
              }`}
            >
              {v === "list" ? "一覧" : "マップ"}
            </button>
          ))}
        </div>
      </div>

      {view === "map" && (
        <CageMap cages={cages ?? []} kpiMap={kpiMap} onSelect={setSelected} />
      )}

      {view === "list" && (
        <div className="space-y-3">
          {isLoading && <p className="text-center text-ocean-300 py-8">読み込み中...</p>}
          {cages?.filter((c) => c.is_active).map((cage) => {
            const kpi = kpiMap.get(cage.id);
            return (
              <div key={cage.id} className="card-ocean p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-bold text-ocean-900">{cage.name}</span>
                      {kpi?.item_label && (
                        <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
                          {kpi.item_label}
                        </span>
                      )}
                    </div>
                    {kpi && (
                      <div className="grid grid-cols-3 gap-2 mt-2">
                        <div className="text-center">
                          <p className="text-[10px] text-ocean-400">推定尾数</p>
                          <p className="text-sm font-semibold text-ocean-800">
                            {kpi.est_count.toLocaleString()}
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-[10px] text-ocean-400">バイオマス</p>
                          <p className="text-sm font-semibold text-ocean-800">
                            {kpi.est_biomass_kg.toFixed(1)}t
                          </p>
                        </div>
                        <div className="text-center">
                          <p className="text-[10px] text-ocean-400">平均体重</p>
                          <p className="text-sm font-semibold text-ocean-800">
                            {(kpi.est_avg_weight_g / 1000).toFixed(2)}kg
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 ml-3">
                    <button
                      onClick={() => setSelected(cage)}
                      className="bg-ocean-600 text-white text-xs font-medium px-3 py-2 rounded-lg hover:bg-ocean-700"
                    >
                      入力
                    </button>
                    <Link
                      href={`/cages/${cage.id}`}
                      className="border border-ocean-200 text-ocean-600 text-xs font-medium px-3 py-2 rounded-lg hover:bg-ocean-50 text-center"
                    >
                      詳細
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {selected && (
        <QuickInputSheet
          cageId={selected.id}
          cageName={selected.name}
          onClose={() => setSelected(null)}
          onSuccess={() => setSelected(null)}
        />
      )}
    </div>
  );
}

// シンプルなグリッドマップ
function CageMap({
  cages,
  kpiMap,
  onSelect,
}: {
  cages: Cage[];
  kpiMap: Map<number, CageKPI>;
  onSelect: (c: Cage) => void;
}) {
  const active = cages.filter((c) => c.is_active);
  return (
    <div className="mb-4">
      <div className="card-ocean p-3 mb-3">
        <p className="text-xs text-ocean-400 mb-1 flex items-center gap-1">
          <MapPin className="w-3 h-3" />
          生簀マップ（色=バイオマス）
        </p>
        <div className="grid grid-cols-5 gap-2">
          {active.map((cage) => {
            const kpi = kpiMap.get(cage.id);
            const biomass = kpi?.est_biomass_kg ?? 0;
            const level =
              biomass > 5000 ? "high" : biomass > 2000 ? "mid" : "low";
            return (
              <button
                key={cage.id}
                onClick={() => onSelect(cage)}
                className={`aspect-square rounded-lg flex flex-col items-center justify-center text-[10px] font-medium transition-transform active:scale-95 ${
                  level === "high"
                    ? "bg-ocean-700 text-white"
                    : level === "mid"
                    ? "bg-ocean-400 text-white"
                    : "bg-ocean-100 text-ocean-600"
                }`}
              >
                <span>{cage.name.replace("いけす", "")}</span>
                {kpi && (
                  <span className="text-[9px] opacity-80">
                    {(biomass / 1000).toFixed(1)}t
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
