"use client";
import { useState } from "react";
import useSWR from "swr";
import { api, Cage } from "@/lib/api";
import { Search } from "lucide-react";
import QuickInputSheet from "@/components/events/QuickInputSheet";

export default function InputPage() {
  const { data: cages } = useSWR("cages", () => api.cages());
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<Cage | null>(null);

  const filtered = cages?.filter(
    (c) =>
      c.is_active &&
      (c.name.includes(query) || c.code.toLowerCase().includes(query.toLowerCase()))
  );

  return (
    <div className="p-4 max-w-lg mx-auto">
      <h1 className="text-xl font-bold text-ocean-900 mb-4">生簀を選んで入力</h1>

      <div className="relative mb-4">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ocean-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="生簀名・コードで絞り込み"
          className="w-full pl-9 pr-4 py-3 border border-ocean-200 rounded-xl bg-white text-ocean-900 placeholder-ocean-300 focus:outline-none focus:ring-2 focus:ring-ocean-400"
        />
      </div>

      <div className="space-y-2">
        {filtered?.map((cage) => (
          <button
            key={cage.id}
            onClick={() => setSelected(cage)}
            className="w-full card-ocean p-4 text-left flex items-center justify-between hover:border-ocean-400 transition-colors active:scale-[0.99]"
          >
            <div>
              <p className="font-semibold text-ocean-900">{cage.name}</p>
              <p className="text-xs text-ocean-400">{cage.code}</p>
            </div>
            <span className="text-ocean-400 text-sm">→</span>
          </button>
        ))}
      </div>

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
