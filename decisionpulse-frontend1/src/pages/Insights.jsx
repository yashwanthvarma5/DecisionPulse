import { useData } from "../context/DataContext";
import Skeleton from "../components/Skeleton";

export default function Insights() {
  const { result } = useData();
  const users = result?.data || [];
  const isLoading = !result;

  const sortedUsers = [...users].sort(
    (a, b) => b.churn_probability - a.churn_probability
  );

  const badge = (risk) => {
    if (risk === "CRITICAL") return "bg-red-600/90 text-white";
    if (risk === "AT_RISK") return "bg-blue-600/90 text-white";
    return "bg-zinc-700 text-white";
  };

  return (
    <div className="space-y-10">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-semibold tracking-tight">User Insights</h2>
        <p className="text-zinc-400 mt-2">
          Detailed churn predictions and recommended actions
        </p>
      </div>

      {/* Loading Skeleton */}
      {isLoading && (
        <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-6">
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="grid grid-cols-5 gap-4 items-center">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-6 w-24 rounded-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-6 mx-auto" />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && users.length === 0 && (
        <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-10 text-center text-zinc-400">
          Upload a CSV file to view user-level insights
        </div>
      )}

      {/* Table */}
      {!isLoading && users.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-zinc-800">
          <table className="w-full text-sm">
            <thead className="bg-zinc-950">
              <tr className="text-left text-zinc-400">
                <th className="p-4">User ID</th>
                <th className="p-4">Churn Probability</th>
                <th className="p-4">Risk Level</th>
                <th className="p-4">Recommended Action</th>
                <th className="p-4 text-center">Anomaly</th>
              </tr>
            </thead>

            <tbody>
              {sortedUsers.map((u) => (
                <tr
                  key={u.user_id}
                  className="border-t border-zinc-800
                             hover:bg-zinc-900/60 transition"
                >
                  <td className="p-4 font-medium">USR-{u.user_id}</td>

                  <td className="p-4 font-medium">
                    {(u.churn_probability * 100).toFixed(1)}%
                  </td>

                  <td className="p-4">
                    <span
                      className={`px-3 py-1 rounded-full
                                  text-xs font-medium ${badge(u.risk_level)}`}
                    >
                      {u.risk_level.replace("_", " ")}
                    </span>
                  </td>

                  <td className="p-4 text-zinc-300 max-w-md">
                    {u.recommended_action}
                  </td>

                  <td className="p-4 text-center">
                    {u.is_anomaly ? (
                      <span
                        title="Anomalous behavior detected"
                        className="text-red-500 font-bold"
                      >
                        ⚠
                      </span>
                    ) : (
                      <span className="text-zinc-500">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
