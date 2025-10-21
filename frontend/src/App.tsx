import { Outlet, Route, Routes } from 'react-router-dom';
import { AppShell } from './components/layout/AppShell';
import { DashboardPage } from './components/pages/DashboardPage';
import { ExerciseWorkspacePage } from './components/pages/ExerciseWorkspacePage';
import { LandingPage } from './components/pages/LandingPage';

const AppRoutes = () => (
  <Routes>
    <Route element={<AppShell />}> 
      <Route index element={<LandingPage />} />
      <Route path="dashboard" element={<DashboardPage />} />
      <Route path="exercise/:exerciseId" element={<ExerciseWorkspacePage />} />
    </Route>
  </Routes>
);

function App() {
  return (
    <div className="min-h-screen">
      <AppRoutes />
    </div>
  );
}

export default App;
