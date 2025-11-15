import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <AppShell>
      <section className="py-20 md:py-32">
        <div className="max-w-5xl mx-auto text-center space-y-12">
          <h1 className="text-7xl md:text-9xl font-bold text-slate-900 leading-tight tracking-tight">
            mirai
          </h1>

          <p className="text-2xl md:text-3xl text-slate-600 max-w-3xl mx-auto font-light">
            Your perfect trip, planned in minutes
          </p>

          <p className="text-lg text-slate-500 max-w-2xl mx-auto">
            Tell us your destination, dates, budget, and vibe. We'll generate a comprehensive
            travel handbook with daily itineraries, budget breakdowns, and insider tips.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
            <Button
              onClick={() => navigate('/plan')}
              size="lg"
              className="bg-sky-400 hover:bg-sky-500 text-white px-10 py-6 text-lg shadow-lg shadow-sky-200/50"
            >
              Start Planning
            </Button>
          </div>
        </div>
      </section>
    </AppShell>
  );
}

