"use client";
import useSWR from "swr";
import { api, SiteSummary, CageKPI } from "@/lib/api";
import { TrendingUp, AlertTriangle, Fish } from "lucide-react";

export default function AnalyticsPage() {
  const { data: summaries, isLoading } = useSWR("kpi-summary", () => api.kpiSummary());

  if (isLoading) return <div className="p-4 text-ocean-300 text-center">読み込み中...</div>;

  const allCages = summaries?.flatMap((s) => s.cages) ?? [];
  const totalBiomass = allCages.reduce((s, c) => s + c.est_biomass_kg, 0);
  const totalCount = allCages.reduce((s, c) => s + c.est_count, 0);
  const highMortCages = allCages.filter(
    (c) => c.mortality_rate_7d !== undefined && c.mortality_rate_7d !== null && c.mortality_rate_7d > 1.0
  );

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-ocean-900 mb-4">分析・KPI</h1>

      {/* 全体サマリー */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="card-ocean p-4">
          <p className="text-xs text-ocean-400 mb-1">総バイオマス</p>
          <p className="text-2xl font-bold text-ocean-800">
            {(totalBiomass / 1000).toFixed(1)}
            <span className="text-sm font-normal ml-1">t</span>
          </p>
        </div>
        <div className="card-ocean p-4">
          <p className="text-xs text-ocean-400 mb-1">総尾数</p>
          <p className="text-2xl font-bold text-ocean-800">
            {totalCount.toLocaleString()}
            <span className="text-sm font-normal ml-1">尾</span>
          </p>
        </div>
      </div>

      {/* アラート */}
      {highMortCages.length > 0 && (
        <div className="mb-6">
          <h2 className="font-semibold text-ocean-800 mb-2 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-500" />
            死亡率警告 (7日 {">"} 1.0%)
          </h2>
          <div className="space-y-2">
            {highMortCages.map((c) => (
              <div key={c.cage_id} className="card-ocean p-3 border-l-4 border-amber-400">
                <p className="font-medium text-ocean-900">{c.cage_name}</p>
                <p className="text-sm text-red-600">死亡率: {c.mortality_rate_7d?.toFixed(2)}%</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* サイト別 */}
      {summaries?.map((site) => (
        <SiteSection key={site.site_id} site={site} />
      ))}
    </div>
  );
}

function SiteSection({ site }: { site: SiteSummary }) {
  return (
    <div className="mb-6">
      <h2 className="font-semibold text-ocean-800 mb-3 flex items-center gap-2">
        <Fish className="w-4 h-4 text-ocean-500" />
        {site.site_name}
      </h2>

      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="card-ocean p-2">
          <p className="text-[10px] text-ocean-400">バイオマス</p>
          <p className="font-bold text-ocean-800">{(site.total_biomass_kg / 1000).toFixed(1)}t</p>
        </div>
        <div className="card-ocean p-2">
          <p className="text-[10px] text-ocean-400">尾数</p>
          <p className="font-bold text-ocean-800">{site.total_est_count.toLocaleString()}</p>
        </div>
        <div className="card-ocean p-2">
          <p className="text-[10px] text-ocean-400">活魚群数</p>
          <p className="font-bold text-ocean-800">{site.active_lot_count}</p>
        </div>
      </div>

      <div className="space-y-2">
        {site.cages.map((c) => (
          <CageRow key={c.cage_id} kpi={c} />
        ))}
      </div>
    </div>
  );
}

function CageRow({ kpi }: { kpi: CageKPI }) {
  const highMort =
    kpi.mortality_rate_7d !== null &&
    kpi.mortality_rate_7d !== undefined &&
    kpi.mortality_rate_7d > 1.0;

  return (
    <div className={`card-ocean p-3 ${highMort ? "border-l-4 border-amber-400" : ""}`}>
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium text-ocean-900">{kpi.cage_name}</span>
        {kpi.item_label && (
          <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
            {kpi.item_label}
          </span>
        )}
      </div>
      <div className="grid grid-cols-4 gap-1 text-center text-xs">
        <div>
          <p className="text-ocean-400">尾数</p>
          <p className="font-semibold text-ocean-800">{kpi.est_count.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-ocean-400">t</p>
          <p className="font-semibold text-ocean-800">{(kpi.est_biomass_kg / 1000).toFixed(2)}</p>
        </div>
        <div>
          <p className="text-ocean-400">死亡率</p>
          <p className={`font-semibold ${highMort ? "text-red-600" : "text-ocean-800"}`}>
            {kpi.mortality_rate_7d?.toFixed(2) ?? "—"}%
          </p>
        </div>
        <div>
          <p className="text-ocean-400">FCR</p>
          <p className="font-semibold text-ocean-800">{kpi.fcr_14d?.toFixed(2) ?? "—"}</p>
        </div>
      </div>
    </div>
  );
}
