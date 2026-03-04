"use client";
import useSWR from "swr";
import { api } from "@/lib/api";
import { useParams } from "next/navigation";
import { ArrowLeft, QrCode } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import QuickInputSheet from "@/components/events/QuickInputSheet";
import KpiCard from "@/components/kpi/KpiCard";
import EventList from "@/components/events/EventList";

export default function CageDetailPage() {
  const { id } = useParams<{ id: string }>();
  const cageId = parseInt(id);
  const { data: cage } = useSWR(`cage-${cageId}`, () => api.cage(cageId));
  const { data: kpi, mutate: mutateKpi } = useSWR(`kpi-cage-${cageId}`, () =>
    api.kpiCage(cageId)
  );
  const { data: events, mutate: mutateEvents } = useSWR(`events-${cageId}`, () =>
    api.events({ cage_id: cageId, limit: 30 })
  );
  const [showInput, setShowInput] = useState(false);

  if (!cage) return <div className="p-4 text-ocean-300">読み込み中...</div>;

  return (
    <div className="max-w-lg mx-auto">
      {/* ヘッダー */}
      <div className="sticky top-0 bg-white border-b border-ocean-100 px-4 py-3 flex items-center gap-3 z-30">
        <Link href="/cages" className="text-ocean-600 hover:text-ocean-800">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="font-bold text-ocean-900">{cage.name}</h1>
          <p className="text-xs text-ocean-400">{cage.code}</p>
        </div>
        <a
          href={`/api/cages/${cageId}/qr`}
          target="_blank"
          className="text-ocean-400 hover:text-ocean-600"
        >
          <QrCode className="w-5 h-5" />
        </a>
        <button
          onClick={() => setShowInput(true)}
          className="bg-ocean-600 text-white text-sm font-medium px-4 py-2 rounded-xl hover:bg-ocean-700"
        >
          入力
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* KPI */}
        {kpi && <KpiCard kpi={kpi} />}

        {/* イベント履歴 */}
        <div>
          <h2 className="font-semibold text-ocean-800 mb-3">作業履歴</h2>
          <EventList events={events ?? []} />
        </div>
      </div>

      {showInput && (
        <QuickInputSheet
          cageId={cageId}
          cageName={cage.name}
          onClose={() => setShowInput(false)}
          onSuccess={() => {
            mutateKpi();
            mutateEvents();
            setShowInput(false);
          }}
        />
      )}
    </div>
  );
}
