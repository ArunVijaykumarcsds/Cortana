import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, CartesianGrid } from "recharts";
import type { Transaction } from "../types";

function bucketByHour(transactions: Transaction[]) {
  const buckets = new Map<string, { hour: string; pass: number; review: number }>();
  const now = new Date();
  for (let i = 11; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 3600000);
    const key = `${d.getHours()}:00`;
    buckets.set(key, { hour: key, pass: 0, review: 0 });
  }
  transactions.forEach((t) => {
    const d = new Date(t.timestamp);
    const key = `${d.getHours()}:00`;
    const b = buckets.get(key);
    if (!b) return;
    if (t.fusion.decision === "REVIEW") b.review += 1;
    else b.pass += 1;
  });
  return Array.from(buckets.values());
}

export default function DecisionTrendChart({ transactions }: { transactions: Transaction[] }) {
  const data = bucketByHour(transactions);
  return (
    <div className="panel p-5">
      <p className="label-eyebrow">Decisions, last 12 hours</p>
      <div className="mt-4 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barCategoryGap={4}>
            <CartesianGrid stroke="#1c1d1a" vertical={false} />
            <XAxis
              dataKey="hour"
              tick={{ fill: "#8b8d84", fontSize: 10, fontFamily: "IBM Plex Mono, monospace" }}
              axisLine={{ stroke: "#2a2b27" }}
              tickLine={false}
              interval={1}
            />
            <YAxis
              tick={{ fill: "#8b8d84", fontSize: 10, fontFamily: "IBM Plex Mono, monospace" }}
              axisLine={false}
              tickLine={false}
              width={24}
            />
            <Tooltip
              contentStyle={{
                background: "#161715",
                border: "1px solid #2a2b27",
                borderRadius: 6,
                fontSize: 12,
                fontFamily: "IBM Plex Mono, monospace",
              }}
              cursor={{ fill: "rgba(255,255,255,0.03)" }}
            />
            <Bar dataKey="pass" stackId="a" fill="#6f9d74" radius={[0, 0, 0, 0]} />
            <Bar dataKey="review" stackId="a" fill="#c0503f" radius={[2, 2, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-2 flex gap-4 text-xs text-mute">
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-(--color-low)" /> Pass
        </span>
        <span className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-(--color-critical)" /> Review
        </span>
      </div>
    </div>
  );
}
