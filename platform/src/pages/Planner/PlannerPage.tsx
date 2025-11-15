import { AppShell } from '@/components/layout/AppShell';
import { TripPlannerForm } from '@/components/planner/TripPlannerForm';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function PlannerPage() {
  const navigate = useNavigate();

  return (
    <AppShell>
      <div className="space-y-8 pb-20">
        {/* Back Button */}
        <div className="flex items-center">
          <Button
            variant="ghost"
            onClick={() => navigate('/')}
            className="text-slate-600 hover:text-slate-900"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Button>
        </div>

        {/* Page Header */}
        <div className="max-w-3xl mx-auto text-center space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold text-slate-900">
            Plan Your Trip
          </h1>
          <p className="text-lg text-slate-600">
            Fill in the details below and let AI create your perfect itinerary
          </p>
        </div>

        {/* Trip Planner Form */}
        <div className="max-w-3xl mx-auto">
          <TripPlannerForm />
        </div>
      </div>
    </AppShell>
  );
}

