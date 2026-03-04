"use client";
import useSWR from "swr";
import { api, TodayTodoItem } from "@/lib/api";
import { AlertCircle, CheckCircle2, Fish, Clock } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import QuickInputSheet from "@/components/events/QuickInputSheet";

function fetcher() {
  return api.todayTodos();
}

function formatLastFeed(iso?: string): string {
  if (!iso) return "未実施";
  const d = new Date(iso);
  const h = d.getHours().toString().padStart(2, "0");
  const m = d.getMinutes().toString().padStart(2, "0");
  const date = `${d.getMonth() + 1}/${d.getDate()}`;
  return `${date} ${h}:${m}`;
}

export default function TodayPage() {
  const { data: todos, isLoading, mutate } = useSWR("today-todos", fetcher, {
    refreshInterval: 60000,
  });
  const { data: kpi } = useSWR("kpi-summary", () => api.kpiSummary());
  const [selectedCage, setSelectedCage] = useState<{ id: number; name: string } | null>(null);

  const today = new Date();
  const dateStr = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`;
  const weekDay = ["日", "月", "火", "水", "木", "金", "土"][today.getDay()];

  const totalBiomass = kpi?.reduce((s, site) => s + site.total_biomass_kg, 0) ?? 0;
  const totalCount = kpi?.reduce((s, site) => s + site.total_est_count, 0) ?? 0;

  return (
    <div className="p-4 max-w-lg mx-auto">
      {/* Header */}
      <div className="mb-6">
        <p className="text-ocean-400 text-sm">{dateStr}（{weekDay}）</p>
        <h1 className="text-2xl font-bold text-ocean-900">今日の作業</h1>
      </div>

      {/* KPI サマリー */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <div className="card-ocean p-4">
          <p className="text-xs text-ocean-400 mb-1">推定バイオマス</p>
          <p className="text-xl font-bold text-ocean-800">
            {totalBiomass.toLocaleString("ja-JP", { maximumFractionDigits: 1 })}
            <span className="text-sm font-normal ml-1">t</span>
          </p>
        </div>
        <div className="card-ocean p-4">
          <p className="text-xs text-ocean-400 mb-1">推定総尾数</p>
          <p className="text-xl font-bold text-ocean-800">
            {totalCount.toLocaleString("ja-JP")}
            <span className="text-sm font-normal ml-1">尾</span>
          </p>
        </div>
      </div>

      {/* ToDoリスト */}
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-semibold text-ocean-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-amber-500" />
          未処理 ({todos?.length ?? "..."})
        </h2>
      </div>

      {isLoading && (
        <div className="text-center py-8 text-ocean-300">読み込み中...</div>
      )}

      {todos?.length === 0 && (
        <div className="card-ocean p-6 text-center">
          <CheckCircle2 className="w-10 h-10 text-teal-500 mx-auto mb-2" />
          <p className="font-semibold text-ocean-800">今日の給餌はすべて完了！</p>
          <p className="text-sm text-ocean-400 mt-1">お疲れさまでした</p>
        </div>
      )}

      <div className="space-y-3">
        {todos?.map((todo: TodayTodoItem) => (
          <div key={todo.cage_id} className="card-ocean p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Fish className="w-4 h-4 text-ocean-500" />
                  <span className="font-semibold text-ocean-900">{todo.cage_name}</span>
                  {todo.item_label && (
                    <span className="text-xs bg-teal-100 text-teal-700 px-2 py-0.5 rounded-full">
                      {todo.item_label}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1 text-xs text-ocean-400">
                  <Clock className="w-3 h-3" />
                  <span>最終給餌: {formatLastFeed(todo.last_feeding_at)}</span>
                </div>
                <div className="flex gap-1 mt-2">
                  {todo.missing_types.map((t) => (
                    <span
                      key={t}
                      className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full"
                    >
                      {t === "FEEDING" ? "給餌未入力" : t}
                    </span>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setSelectedCage({ id: todo.cage_id, name: todo.cage_name })}
                className="ml-3 bg-ocean-600 text-white text-sm font-medium px-4 py-2 rounded-xl hover:bg-ocean-700 transition-colors whitespace-nowrap"
              >
                入力
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* QuickInput BottomSheet */}
      {selectedCage && (
        <QuickInputSheet
          cageId={selectedCage.id}
          cageName={selectedCage.name}
          onClose={() => setSelectedCage(null)}
          onSuccess={() => {
            mutate();
            setSelectedCage(null);
          }}
        />
      )}
    </div>
  );
}
