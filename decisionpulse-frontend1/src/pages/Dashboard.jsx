import { useData } from "../context/DataContext";
import RiskDistribution from "../components/RiskDistribution";
import Skeleton from "../components/Skeleton";
import { Users, Percent, AlertTriangle, Activity } from "lucide-react";

export default function Dashboard() {
  const { result, loading } = useData();
  const users = result?.data || [];

  const totalUsers = users.length;

  const avgChurn =
    totalUsers === 0
      ? "0%"
      : (
          (users.reduce((sum, u) => sum + u.churn_probability, 0) /
            totalUsers) *
          100
        ).toFixed(1) + "%";

  const criticalUsers = users.filter((u) => u.risk_level === "CRITICAL").length;
  const anomalies = users.filter((u) => u.is_anomaly).length;

  const stats = [
    { label: "Total Users Analyzed", value: totalUsers, icon: Users },
    { label: "Average Churn Probability", value: avgChurn, icon: Percent },
    { label: "Critical Risk Users", value: criticalUsers, icon: AlertTriangle },
    { label: "Anomalies Detected", value: anomalies, icon: Activity },
  ];

  const distribution = [
    {
      label: "Healthy",
      count: users.filter((u) => u.risk_level === "HEALTHY").length,
    },
    {
      label: "At Risk",
      count: users.filter((u) => u.risk_level === "AT_RISK").length,
    },
    {
      label: "Critical",
      count: users.filter((u) => u.risk_level === "CRITICAL").length,
    },
  ];

  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-zinc-400 mt-2">
          Overview of user behavior analytics and churn insights
        </p>
      </div>

      {/* 1️⃣ No upload yet */}
      {!result && !loading && (
        <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-10 text-center text-zinc-400">
          Upload a CSV file to get started
        </div>
      )}

      {/* 2️⃣ Upload in progress */}
      {loading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="rounded-xl bg-zinc-950 border border-zinc-800 p-6 space-y-4"
              >
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-8 w-1/3" />
              </div>
            ))}
          </div>

          <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-6 h-[350px]">
            <Skeleton className="h-5 w-48 mb-6" />
            <Skeleton className="h-full w-full" />
          </div>
        </>
      )}

      {/* 3️⃣ Data ready */}
      {result && !loading && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
            {stats.map((item) => (
              <div
                key={item.label}
                className="rounded-xl bg-gradient-to-br from-zinc-950 to-zinc-900
                           border border-zinc-800 p-6
                           hover:border-zinc-700 transition"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm text-zinc-400">{item.label}</p>
                  <item.icon className="h-5 w-5 text-zinc-500" />
                </div>

                <p className="text-3xl font-semibold mt-3">{item.value}</p>
              </div>
            ))}
          </div>

          <RiskDistribution data={distribution} />
        </>
      )}
    </div>
  );
}
