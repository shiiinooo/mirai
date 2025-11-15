import { Trip } from '@/types/trip';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Calendar, Users, Sparkles } from 'lucide-react';
import { format } from 'date-fns';

interface TripOverviewProps {
  trip: Trip;
}

export function TripOverview({ trip }: TripOverviewProps) {
  return (
    <Card className="bg-white border-slate-200 shadow-lg">
      <CardHeader>
        <CardTitle className="text-lg text-slate-900">Trip Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-start gap-3">
          <MapPin className="h-5 w-5 text-sky-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-slate-600">Destination</p>
            <p className="text-sm font-medium text-slate-900">{trip.destination}</p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Calendar className="h-5 w-5 text-sky-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-slate-600">Dates</p>
            <p className="text-sm font-medium text-slate-900">
              {format(new Date(trip.startDate), 'MMM d')} -{' '}
              {format(new Date(trip.endDate), 'MMM d, yyyy')}
            </p>
            <p className="text-xs text-slate-500">
              {trip.days.length} {trip.days.length === 1 ? 'day' : 'days'}
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Users className="h-5 w-5 text-sky-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-slate-600">Travelers</p>
            <p className="text-sm font-medium text-slate-900">
              {trip.adults} {trip.adults === 1 ? 'adult' : 'adults'}
              {trip.children > 0 && `, ${trip.children} ${trip.children === 1 ? 'child' : 'children'}`}
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <Sparkles className="h-5 w-5 text-sky-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-slate-600">Generated</p>
            <p className="text-sm font-medium text-slate-900">
              {format(new Date(trip.createdAt), 'MMM d, yyyy')}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
