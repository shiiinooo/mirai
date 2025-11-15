import { useState, useRef, useEffect } from 'react';
import { Day } from '@/types/trip';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Sunrise, Sun, Moon, Lightbulb, Volume2, VolumeX, Loader2 } from 'lucide-react';
import { getActivityAudio } from '@/lib/api/activities';

interface DayCardProps {
  day: Day;
}

const categoryColors = {
  culture: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  food: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  nature: 'bg-green-500/10 text-green-400 border-green-500/20',
  nightlife: 'bg-pink-500/10 text-pink-400 border-pink-500/20',
  shopping: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  relaxation: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  adventure: 'bg-red-500/10 text-red-400 border-red-500/20',
};

const timeOfDayConfig = [
  { key: 'morning' as const, icon: Sunrise, label: 'Morning', color: 'text-amber-400' },
  { key: 'afternoon' as const, icon: Sun, label: 'Afternoon', color: 'text-orange-400' },
  { key: 'evening' as const, icon: Moon, label: 'Evening', color: 'text-indigo-400' },
];

interface ActivityAudioState {
  [activityId: string]: {
    isLoading: boolean;
    isPlaying: boolean;
    audio: HTMLAudioElement | null;
    error: string | null;
  };
}

export function DayCard({ day }: DayCardProps) {
  const [audioStates, setAudioStates] = useState<ActivityAudioState>({});
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement | null }>({});

  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      Object.values(audioRefs.current).forEach((audio) => {
        if (audio) {
          audio.pause();
          audio.src = '';
        }
      });
    };
  }, []);

  const handlePlayAudio = async (activityId: string, story: string) => {
    const currentState = audioStates[activityId];
    
    // If audio is already loaded and playing, pause it
    if (currentState?.isPlaying && currentState.audio) {
      currentState.audio.pause();
      setAudioStates((prev) => ({
        ...prev,
        [activityId]: { ...prev[activityId], isPlaying: false },
      }));
      return;
    }

    // If audio is already loaded but paused, resume it
    if (currentState?.audio && !currentState.isPlaying) {
      currentState.audio.play();
      setAudioStates((prev) => ({
        ...prev,
        [activityId]: { ...prev[activityId], isPlaying: true },
      }));
      return;
    }

    // Load and play new audio
    setAudioStates((prev) => ({
      ...prev,
      [activityId]: { isLoading: true, isPlaying: false, audio: null, error: null },
    }));

    try {
      const audioBlob = await getActivityAudio(activityId, story);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      // Set up event listeners
      audio.onended = () => {
        setAudioStates((prev) => ({
          ...prev,
          [activityId]: { ...prev[activityId], isPlaying: false },
        }));
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setAudioStates((prev) => ({
          ...prev,
          [activityId]: {
            ...prev[activityId],
            isLoading: false,
            isPlaying: false,
            error: 'Failed to play audio',
          },
        }));
        URL.revokeObjectURL(audioUrl);
      };

      audio.onplay = () => {
        setAudioStates((prev) => ({
          ...prev,
          [activityId]: { ...prev[activityId], isPlaying: true, isLoading: false },
        }));
      };

      audioRefs.current[activityId] = audio;
      
      // Play audio
      await audio.play();

      setAudioStates((prev) => ({
        ...prev,
        [activityId]: {
          isLoading: false,
          isPlaying: true,
          audio,
          error: null,
        },
      }));
    } catch (error) {
      setAudioStates((prev) => ({
        ...prev,
        [activityId]: {
          isLoading: false,
          isPlaying: false,
          audio: null,
          error: error instanceof Error ? error.message : 'Failed to load audio',
        },
      }));
    }
  };

  return (
    <Card className="bg-white border-slate-200 shadow-lg border-l-4 border-l-sky-400">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-xl text-slate-900">{day.title}</CardTitle>
            {day.description && (
              <p className="text-sm text-slate-600 mt-1">{day.description}</p>
            )}
          </div>
          <Badge variant="outline" className="border-slate-200 text-slate-700">
            Day {day.dayNumber}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {timeOfDayConfig.map(({ key, icon: Icon, label, color }) => {
          const activities = day.schedule[key];
          if (!activities || activities.length === 0) return null;

          return (
            <div key={key} className="space-y-3">
              <div className="flex items-center gap-2">
                <Icon className={`h-5 w-5 ${color}`} />
                <h4 className="font-semibold text-slate-900">{label}</h4>
              </div>

              <div className="space-y-3 ml-7">
                {activities.map((activity) => (
                  <div
                    key={activity.id}
                    className="p-4 rounded-lg bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <h5 className="font-medium text-slate-900">{activity.name}</h5>
                          {activity.category && (
                            <Badge
                              variant="outline"
                              className={categoryColors[activity.category]}
                            >
                              {activity.category}
                            </Badge>
                          )}
                          {activity.tags?.map((tag) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="border-slate-200 text-slate-600 text-xs"
                            >
                              {tag}
                            </Badge>
                          ))}
                        </div>

                        {/* Description and story text are not displayed - only audio icon for story playback */}
                        
                        <div className="flex items-center gap-4 text-xs text-slate-600">
                          {activity.duration && <span>⏱ {activity.duration}</span>}
                          {activity.time && <span>🕐 {activity.time}</span>}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {activity.story && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handlePlayAudio(activity.id, activity.story!)}
                            disabled={audioStates[activity.id]?.isLoading}
                            className="h-8 w-8 p-0"
                            title={
                              audioStates[activity.id]?.isPlaying
                                ? 'Pause story'
                                : 'Play story'
                            }
                          >
                            {audioStates[activity.id]?.isLoading ? (
                              <Loader2 className="h-4 w-4 animate-spin text-sky-600" />
                            ) : audioStates[activity.id]?.isPlaying ? (
                              <VolumeX className="h-4 w-4 text-sky-600" />
                            ) : (
                              <Volume2 className="h-4 w-4 text-sky-600" />
                            )}
                          </Button>
                        )}
                        {activity.cost !== undefined && activity.cost > 0 && (
                          <div className="text-right">
                            <span className="text-sm font-medium text-sky-600">
                              ${activity.cost}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {day.travelTip && (
          <div className="mt-4 p-4 rounded-lg bg-sky-50 border border-sky-200">
            <div className="flex items-start gap-2">
              <Lightbulb className="h-4 w-4 text-sky-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-sky-600 mb-1">Travel Tip</p>
                <p className="text-sm text-slate-600">{day.travelTip}</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
