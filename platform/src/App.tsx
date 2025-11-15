import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { LandingPage } from '@/pages/Landing/LandingPage';
import { PlannerPage } from '@/pages/Planner/PlannerPage';
import { TripPage } from '@/pages/Trip/TripPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/plan" element={<PlannerPage />} />
        <Route path="/trip/:id" element={<TripPage />} />
        <Route path="/demo" element={<Navigate to="/trip/demo" replace />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
