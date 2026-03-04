"use client";
import { CageKPI } from "@/lib/api";
import { TrendingUp, TrendingDown, AlertTriangle } from "lucide-react";

export default function KpiCard({ kpi }: { kpi: CageKPI }) {
  const hasMortality = kpi.mortality_rate_7d !== null && kpi.mortality_rate_7d !== undefined;
  const highMortality = hasMortality && kpi.mortality_rate_7d! > 1.0;

  return (
    <div className="card-ocean p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-ocean-800">KPI</h3>
        {kpi.item_label && (
          <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
            {kpi.item_label}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <KpiItem
          label="推定尾数"
          value={kpi.est_count.toLocaleString("ja-JP")}
          unit="尾"
        />
        <KpiItem
          label="推定バイオマス"
          value={kpi.est_biomass_kg.toFixed(1)}
          unit="t"
        />
        <KpiItem
          label="平均体重"
          value={(kpi.est_avg_weight_g / 1000).toFixed(2)}
          unit="kg"
        />
        <KpiItem
          label="死亡率(7日)"
          value={hasMortality ? kpi.mortality_rate_7d!.toFixed(2) : "—"}
          unit="%"
          alert={highMortality}
        />
        <KpiItem
          label={`FCR(14日)${kpi.is_fcr_estimated ? " *推定" : ""}`}
          value={kpi.fcr_14d?.toFixed(2) ?? "—"}
        />
        <KpiItem
          label="SGR(%/日)"
          value={kpi.sgr?.toFixed(3) ?? "—"}
          positive={kpi.sgr !== null && kpi.sgr !== undefined && kpi.sgr > 0}
        />
      </div>

      {kpi.days_to_target && (
        <div className="mt-3 bg-ocean-50 rounded-xl px-3 py-2">
          <p className="text-xs text-ocean-500">
            出荷見込み: <span className="font-semibold text-ocean-800">約 {kpi.days_to_target} 日後</span>
            （目標{(kpi.target_weight_g / 1000).toFixed(1)}kg）
          </p>
        </div>
      )}
    </div>
  );
}

function KpiItem({
  label,
  value,
  unit,
  alert,
  positive,
}: {
  label: string;
  value: string;
  unit?: string;
  alert?: boolean;
  positive?: boolean;
}) {
  return (
    <div className="bg-ocean-50 rounded-xl p-3">
      <p className="text-[10px] text-ocean-400 mb-0.5">{label}</p>
      <div className="flex items-center gap-1">
        <span className={`text-lg font-bold ${alert ? "text-red-600" : "text-ocean-900"}`}>
          {value}
        </span>
        {unit && <span className="text-xs text-ocean-400">{unit}</span>}
        {alert && <AlertTriangle className="w-3 h-3 text-red-500" />}
        {positive && !alert && <TrendingUp className="w-3 h-3 text-teal-500" />}
      </div>
    </div>
  );
}
