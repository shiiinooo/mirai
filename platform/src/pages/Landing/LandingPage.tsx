import { AppShell } from '@/components/layout/AppShell';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <AppShell>
      <section className="min-h-screen flex items-center justify-center py-8 md:py-12">
        <div className="max-w-5xl mx-auto text-center space-y-6 md:space-y-8 w-full px-4">
          <h1 className="text-6xl md:text-8xl font-bold text-slate-900 leading-tight tracking-tight">
            mirai
          </h1>

          <p className="text-xl md:text-2xl text-slate-600 max-w-3xl mx-auto font-light">
            Your perfect trip, planned in minutes
          </p>

          <p className="text-base md:text-lg text-slate-500 max-w-2xl mx-auto">
            Tell us your destination, dates, budget, and vibe. We'll generate a comprehensive
            travel handbook with daily itineraries, budget breakdowns, and insider tips.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-4">
            <Button
              onClick={() => navigate('/plan')}
              size="lg"
              className="bg-sky-400 hover:bg-sky-500 text-white px-10 py-6 text-lg shadow-lg shadow-sky-200/50"
            >
              Start Planning
            </Button>
          </div>

          {/* Partners Section */}
          <div className="pt-8 md:pt-10 space-y-4">
            <p className="text-xs md:text-sm font-medium text-slate-400 uppercase tracking-wider">
              Special Thanks to Our Partners
            </p>
            <div className="flex flex-wrap justify-center items-center gap-4 md:gap-6">
              <a
                href="https://mistral.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:text-sky-500 transition-colors duration-200 font-semibold text-sm md:text-base"
              >
                Mistral AI
              </a>
              <span className="text-slate-300">•</span>
              <a
                href="https://qdrant.tech"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:text-sky-500 transition-colors duration-200 font-semibold text-sm md:text-base"
              >
                Qdrant
              </a>
              <span className="text-slate-300">•</span>
              <a
                href="https://cloud.google.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:text-sky-500 transition-colors duration-200 font-semibold text-sm md:text-base"
              >
                Google Cloud
              </a>
              <span className="text-slate-300">•</span>
              <a
                href="https://lovable.dev"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:text-sky-500 transition-colors duration-200 font-semibold text-sm md:text-base"
              >
                Lovable
              </a>
              <span className="text-slate-300">•</span>
              <a
                href="https://elevenlabs.io"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-600 hover:text-sky-500 transition-colors duration-200 font-semibold text-sm md:text-base"
              >
                ElevenLabs
              </a>
            </div>
          </div>
        </div>
      </section>
    </AppShell>
  );
}

