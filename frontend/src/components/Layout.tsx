import { Banknote, CalendarClock, Leaf, Sprout, Users } from "lucide-react";
import type { ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/employees", label: "Employees", icon: Users },
  { to: "/attendance", label: "Attendance", icon: CalendarClock },
  { to: "/pakyaw", label: "Pakyaw Entry", icon: Sprout },
  { to: "/payroll", label: "Payroll", icon: Banknote },
];

function SidebarLink({ to, label, icon: Icon }: { to: string; label: string; icon: typeof Users }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          isActive
            ? "bg-green-100 text-green-900"
            : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
        }`
      }
    >
      <Icon size={18} />
      {label}
    </NavLink>
  );
}

export default function Layout({ children }: { children?: ReactNode }) {
  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-60 flex-shrink-0 flex-col border-r border-slate-200 bg-white px-3 py-4">
        <div className="mb-6 flex items-center gap-2 px-2">
          <Leaf className="text-green-700" size={24} />
          <div>
            <p className="text-sm font-semibold leading-tight text-slate-900">Bio Green</p>
            <p className="text-xs leading-tight text-slate-500">HR &amp; Payroll</p>
          </div>
        </div>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">{children ?? <Outlet />}</main>
    </div>
  );
}
