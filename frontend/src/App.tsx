import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AttendanceEntry from "./pages/AttendanceEntry";
import Dashboard from "./pages/Dashboard";
import EmployeeDirectory from "./pages/EmployeeDirectory";
import PakyawEntry from "./pages/PakyawEntry";
import PayrollGeneration from "./pages/PayrollGeneration";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="/employees" element={<EmployeeDirectory />} />
        <Route path="/attendance" element={<AttendanceEntry />} />
        <Route path="/pakyaw" element={<PakyawEntry />} />
        <Route path="/payroll" element={<PayrollGeneration />} />
      </Route>
    </Routes>
  );
}
