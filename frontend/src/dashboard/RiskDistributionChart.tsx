import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import type { Transaction } from "../types";
import { RISK_COLOR_VAR, RISK_LABEL } from "../utils/risk";
import type { RiskLevel } from "../types";

const LEVELS: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function RiskDistributionChart({ transactions }: { transactions: Transaction[] }) {
  const data = LEVELS.map((level) => ({
    name: RISK_LABEL[level],
    level,
    value: transactions.filter((t) => t.fusion.risk_level === level).length,
  }));

  return (
    <div className="panel p-5">
      <p className="label-eyebrow">Risk distribution</p>
      <div className="mt-2 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius="60%"
              outerRadius="90%"
              paddingAngle={3}
              stroke="none"
            >
              {data.map((d) => (
                <Cell key={d.level} fill={RISK_COLOR_VAR[d.level]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                background: "#161715",
                border: "1px solid #2a2b27",
                borderRadius: 6,
                fontSize: 12,
                fontFamily: "IBM Plex Mono, monospace",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2">
        {data.map((d) => (
          <div key={d.level} className="flex items-center gap-2 text-xs text-mute">
            <span
              className="h-2 w-2 rounded-full"
              style={{ background: RISK_COLOR_VAR[d.level] }}
              aria-hidden="true"
            />
            {d.name}
            <span className="data-num ml-auto text-ivory-dim">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
