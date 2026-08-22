import { NavLink } from "react-router-dom";
import {
  LayoutGrid,
  ArrowLeftRight,
  BellRing,
  FolderSearch,
  BrainCircuit,
  Settings2,
} from "lucide-react";

const ITEMS = [
  { to: "/app", label: "Command Center", icon: LayoutGrid, end: true },
  { to: "/app/transactions", label: "Transactions", icon: ArrowLeftRight },
  { to: "/app/alerts", label: "Alerts", icon: BellRing },
  { to: "/app/investigations", label: "Investigations", icon: FolderSearch },
  { to: "/app/model-intelligence", label: "Model Intelligence", icon: BrainCircuit },
  { to: "/app/system", label: "System", icon: Settings2 },
];

export default function Navigation() {
  return (
    <>
      {/* Desktop sidebar */}
      <nav
        className="hidden w-60 shrink-0 flex-col border-r border-hairline bg-void px-3 py-6 md:flex"
        aria-label="Primary"
      >
        <a href="/" className="mb-8 flex items-center gap-2 px-2">
          <span className="font-display text-lg tracking-wide text-ivory">CORTANA</span>
        </a>
        <ul className="flex flex-col gap-1">
          {ITEMS.map(({ to, label, icon: Icon, end }) => (
            <li key={to}>
              <NavLink
                to={to}
                end={end}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
                    isActive
                      ? "bg-surface-2 text-ivory"
                      : "text-mute hover:bg-surface-2/60 hover:text-ivory-dim"
                  }`
                }
              >
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
                {label}
              </NavLink>
            </li>
          ))}
        </ul>
        <div className="mt-auto px-2 pt-6">
          <p className="label-eyebrow">Release</p>
          <p className="mt-1 text-xs text-mute">CORTANA_FINAL_v1.0.0</p>
        </div>
      </nav>

      {/* Mobile bottom nav */}
      <nav
        className="fixed inset-x-0 bottom-0 z-40 flex border-t border-hairline bg-void/95 backdrop-blur md:hidden"
        aria-label="Primary"
        style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
      >
        {ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-1 flex-col items-center gap-1 py-2.5 text-[10px] ${
                isActive ? "text-ivory" : "text-mute"
              }`
            }
          >
            <Icon className="h-[18px] w-[18px]" aria-hidden="true" />
            <span className="truncate px-0.5">{label.split(" ")[0]}</span>
          </NavLink>
        ))}
      </nav>
    </>
  );
}
