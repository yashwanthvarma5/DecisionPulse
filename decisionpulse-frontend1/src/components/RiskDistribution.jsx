import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const COLORS = {
  Healthy: "#71717a",
  "At Risk": "#3b82f6",
  Critical: "#ef4444",
};

/* ✅ Custom Tooltip */
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="bg-zinc-900 border border-zinc-700 rounded-lg px-4 py-3 shadow-lg">
      <p className="text-sm font-semibold text-white">{label}</p>
      <p className="text-sm text-zinc-300 mt-1">
        Count:{" "}
        <span className="text-white font-medium">{payload[0].value}</span>
      </p>
    </div>
  );
}

export default function RiskDistribution({ data }) {
  return (
    <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-6 h-[360px]">
      <h3 className="text-lg font-semibold mb-6">Risk Distribution</h3>

      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} barSize={64}>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#27272a"
            vertical={false}
          />

          <XAxis
            dataKey="label"
            stroke="#a1a1aa"
            tickLine={false}
            axisLine={false}
          />

          <YAxis
            stroke="#a1a1aa"
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
          />

          {/* ✅ FIXED TOOLTIP */}
          <Tooltip content={<CustomTooltip />} />

          <Bar dataKey="count" radius={[8, 8, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[entry.label]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
