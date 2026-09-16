import { Banknote, CalendarClock, Sprout, Users } from "lucide-react";
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
        <div className="mb-6 px-2">
          <img
            src="/logo.png"
            alt="Bio Green Processing and Manufacturing Inc."
            className="w-full mix-blend-multiply"
          />
          <p className="mt-1 text-xs font-medium leading-tight text-slate-500">HR &amp; Payroll</p>
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
