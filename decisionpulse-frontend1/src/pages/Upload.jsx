import { useState } from "react";
import { useData } from "../context/DataContext";
import { UploadCloud } from "lucide-react";

export default function Upload() {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  const { setResult, loading, setLoading } = useData();

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a CSV file");
      return;
    }

    setError("");
    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/upload-data", {
        method: "POST",
        body: formData,
      });

      const json = await res.json();
      if (!res.ok) throw new Error("Invalid CSV");

      setResult(json);
    } catch {
      setError("Upload failed. Please check the CSV format.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-10 max-w-2xl">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-semibold tracking-tight">Upload Data</h2>
        <p className="text-zinc-400 mt-2">
          Import user behavior data for churn analysis
        </p>
      </div>

      {/* Upload Card */}
      <div className="rounded-xl bg-zinc-950 border border-zinc-800 p-6 space-y-6">
        {/* File Drop */}
        <div className="border-2 border-dashed border-zinc-700 rounded-lg p-8 text-center space-y-3">
          <UploadCloud className="mx-auto h-8 w-8 text-zinc-500" />

          <input
            type="file"
            accept=".csv"
            disabled={loading}
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm text-zinc-300
                       file:mr-4 file:py-2 file:px-4
                       file:rounded file:border-0
                       file:bg-zinc-800 file:text-white
                       hover:file:bg-zinc-700
                       disabled:opacity-60"
          />

          {file && (
            <p className="text-sm text-zinc-400">
              Selected file:{" "}
              <span className="text-white font-medium">{file.name}</span>
            </p>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="text-sm text-red-400 bg-red-950/40 border border-red-900 rounded-lg p-3">
            {error}
          </div>
        )}

        {/* CSV Format */}
        <div className="text-xs text-zinc-400 leading-relaxed">
          <p className="font-medium text-zinc-300 mb-1">
            Expected CSV columns:
          </p>
          <code className="block bg-zinc-900 rounded p-3 text-zinc-300 text-xs overflow-x-auto">
            user_id, total_sessions, avg_session_duration, active_days,
            daily_activity_std, sessions_per_day, active_days_ratio,
            days_since_last_active, sessions_last_7d, sessions_prev_7d,
            session_trend_ratio, feature_entropy, unique_features_used
          </code>
        </div>

        {/* Button */}
        <button
          onClick={handleUpload}
          disabled={loading}
          className="w-full px-4 py-2 rounded-lg bg-white text-black
                     font-medium hover:bg-zinc-200
                     disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Processing data..." : "Upload CSV"}
        </button>
      </div>
    </div>
  );
}
