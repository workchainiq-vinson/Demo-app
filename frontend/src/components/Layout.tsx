import { Banknote, CalendarClock, LayoutDashboard, Sprout, Users } from "lucide-react";
import type { ReactNode } from "react";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/employees", label: "Employees", icon: Users, end: false },
  { to: "/attendance", label: "Attendance", icon: CalendarClock, end: false },
  { to: "/pakyaw", label: "Pakyaw Entry", icon: Sprout, end: false },
  { to: "/payroll", label: "Payroll", icon: Banknote, end: false },
];

function SidebarLink({
  to,
  label,
  icon: Icon,
  end,
}: {
  to: string;
  label: string;
  icon: typeof Users;
  end: boolean;
}) {
  return (
    <NavLink
      to={to}
      end={end}
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
      <aside className="flex w-60 flex-shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-100 px-4 py-5">
          <img
            src="/logo.png"
            alt="Bio Green Processing and Manufacturing Inc."
            className="w-full mix-blend-multiply"
          />
          <p className="mt-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            HR &amp; Payroll System
          </p>
        </div>
        <nav className="flex flex-col gap-1 px-3 py-4">
          <p className="mb-1 px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-400">Menu</p>
          {navItems.map((item) => (
            <SidebarLink key={item.to} {...item} />
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-6">{children ?? <Outlet />}</main>
    </div>
  );
}
