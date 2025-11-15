import { useState, useEffect } from 'react';
import { Loader2, Plane, MapPin, Sparkles, Compass } from 'lucide-react';

const loadingPhrases = [
  'Generating your perfect travel itinerary...',
  'Choosing the best destinations for you...',
  'Finding amazing activities and experiences...',
  'Selecting accommodations that match your style...',
  'Planning your daily schedule...',
  'Calculating the perfect budget breakdown...',
  'Discovering hidden gems and local tips...',
  'Crafting your personalized travel handbook...',
  'Optimizing your route and timing...',
  'Gathering insider knowledge...',
];

export function TripPlanningLoading() {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhraseIndex((prev) => (prev + 1) % loadingPhrases.length);
    }, 2500); // Change phrase every 2.5 seconds

    return () => clearInterval(interval);
  }, []);

  const icons = [Plane, MapPin, Sparkles, Compass];
  const CurrentIcon = icons[currentPhraseIndex % icons.length];

  return (
    <div className="fixed inset-0 bg-gradient-to-b from-sky-50 to-white z-[9999] flex items-center justify-center">
      <div className="text-center space-y-8 px-4 max-w-2xl mx-auto">
        {/* Animated Icon */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-sky-200/30 rounded-full blur-2xl animate-pulse" />
            <div className="relative bg-white rounded-full p-8 shadow-xl">
              <CurrentIcon className="h-16 w-16 text-sky-500 animate-pulse" />
            </div>
          </div>
        </div>

        {/* Rotating Phrase */}
        <div className="h-20 flex items-center justify-center">
          <p
            key={currentPhraseIndex}
            className="text-2xl md:text-3xl font-semibold text-slate-900 transition-all duration-500 ease-in-out"
            style={{
              animation: 'fadeInOut 2.5s ease-in-out',
            }}
          >
            {loadingPhrases[currentPhraseIndex]}
          </p>
        </div>

        {/* Loading Spinner */}
        <div className="flex justify-center">
          <Loader2 className="h-8 w-8 text-sky-500 animate-spin" />
        </div>

        {/* Progress Dots */}
        <div className="flex justify-center gap-2">
          {loadingPhrases.map((_, index) => (
            <div
              key={index}
              className={`h-2 w-2 rounded-full transition-all duration-300 ${
                index === currentPhraseIndex
                  ? 'bg-sky-500 w-8'
                  : 'bg-sky-200'
              }`}
            />
          ))}
        </div>

        {/* Subtle Message */}
        <p className="text-sm text-slate-500 mt-8">
          This may take a minute while we create something special for you...
        </p>
      </div>
    </div>
  );
}

