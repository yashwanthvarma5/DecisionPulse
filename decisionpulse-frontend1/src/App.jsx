import { useState } from "react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Insights from "./pages/Insights";

export default function App() {
  const [active, setActive] = useState("Dashboard");

  return (
    <div className="flex min-h-screen bg-black text-white">
      {/* Sidebar */}
      <Sidebar active={active} setActive={setActive} />

      {/* Main Content */}
      <main
        className="flex-1 bg-zinc-900
                   px-8 py-6
                   overflow-y-auto"
      >
        {active === "Dashboard" && <Dashboard />}
        {active === "Upload" && <Upload />}
        {active === "Insights" && <Insights />}
      </main>
    </div>
  );
}
