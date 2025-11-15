import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-50 to-white relative">
      <div className="absolute inset-0 bg-gradient-radial pointer-events-none" />

      <div className="relative">
        <header className="border-b border-slate-200/50 backdrop-blur-sm sticky top-0 z-50 bg-white/80">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <Link to="/" className="group">
                <span className="text-2xl font-bold text-slate-900">mirai</span>
              </Link>

              <p className="hidden sm:block text-sm text-slate-600">
                AI-powered travel planning
              </p>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
