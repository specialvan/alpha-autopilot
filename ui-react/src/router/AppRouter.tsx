import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { App as DashboardPage } from '../App';
import { V2WorkbenchPage } from '../pages/V2WorkbenchPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/v2/workbench" element={<V2WorkbenchPage />} />
    </Routes>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
