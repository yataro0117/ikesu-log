"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Grid3x3, Plus, BarChart2, Package } from "lucide-react";

const tabs = [
  { href: "/today", label: "今日", icon: Home },
  { href: "/cages", label: "生簀", icon: Grid3x3 },
  { href: "/input", label: "入力", icon: Plus, primary: true },
  { href: "/analytics", label: "分析", icon: BarChart2 },
  { href: "/harvest", label: "出荷", icon: Package },
];

export default function TabBar() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-ocean-100 safe-bottom z-40">
      <div className="flex h-16">
        {tabs.map(({ href, label, icon: Icon, primary }) => {
          const active = pathname.startsWith(href);
          if (primary) {
            return (
              <Link
                key={href}
                href={href}
                className="flex-1 flex flex-col items-center justify-center"
              >
                <div className="w-12 h-12 rounded-full bg-ocean-600 flex items-center justify-center shadow-lg -mt-4">
                  <Icon className="w-6 h-6 text-white" strokeWidth={2.5} />
                </div>
              </Link>
            );
          }
          return (
            <Link
              key={href}
              href={href}
              className={`flex-1 flex flex-col items-center justify-center gap-0.5 transition-colors ${
                active ? "text-ocean-600" : "text-ocean-300"
              }`}
            >
              <Icon className="w-5 h-5" strokeWidth={active ? 2.5 : 2} />
              <span className="text-[10px] font-medium">{label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
