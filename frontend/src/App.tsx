import { Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import AttendanceEntry from "./pages/AttendanceEntry";
import Dashboard from "./pages/Dashboard";
import DeductionManagement from "./pages/DeductionManagement";
import EmployeeDirectory from "./pages/EmployeeDirectory";
import PakyawEntry from "./pages/PakyawEntry";
import PayrollGeneration from "./pages/PayrollGeneration";
import ShiftManagement from "./pages/ShiftManagement";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="/employees" element={<EmployeeDirectory />} />
        <Route path="/shifts" element={<ShiftManagement />} />
        <Route path="/attendance" element={<AttendanceEntry />} />
        <Route path="/pakyaw" element={<PakyawEntry />} />
        <Route path="/deductions" element={<DeductionManagement />} />
        <Route path="/payroll" element={<PayrollGeneration />} />
      </Route>
    </Routes>
  );
}
