import { LayoutDashboard, UploadCloud, BarChart3 } from "lucide-react";

export default function Sidebar({ active, setActive }) {
  const items = [
    {
      name: "Dashboard",
      icon: LayoutDashboard,
    },
    {
      name: "Upload",
      icon: UploadCloud,
    },
    {
      name: "Insights",
      icon: BarChart3,
    },
  ];

  return (
    <aside className="w-64 bg-zinc-950 border-r border-zinc-800 p-6">
      {/* Brand */}
      <h1 className="text-xl font-semibold mb-10 tracking-tight">
        DecisionPulse
      </h1>

      {/* Navigation */}
      <nav className="space-y-2">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = active === item.name;

          return (
            <button
              key={item.name}
              onClick={() => setActive(item.name)}
              className={`
                w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm
                transition
                ${
                  isActive
                    ? "bg-zinc-800 text-white shadow-inner"
                    : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
                }
              `}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
