import { Trip } from '@/types/trip';
import { MapPin, Calendar, Users } from 'lucide-react';
import { format } from 'date-fns';

interface TripHeaderProps {
  trip: Trip;
}

export function TripHeader({ trip }: TripHeaderProps) {
  const startDate = new Date(trip.startDate);
  const endDate = new Date(trip.endDate);
  const duration = trip.days.length;

  return (
    <div className="bg-gradient-to-r from-sky-400 to-blue-400 rounded-xl p-6 shadow-lg">
      <div className="space-y-3">
        <h1 className="text-3xl md:text-4xl font-bold text-white">{trip.destination}</h1>

        <div className="flex flex-wrap gap-4 text-sm text-white/90">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-white" />
            <span>
              {format(startDate, 'MMM d')} - {format(endDate, 'MMM d, yyyy')} ({duration}{' '}
              {duration === 1 ? 'day' : 'days'})
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-white" />
            <span>
              {trip.adults} {trip.adults === 1 ? 'adult' : 'adults'}
              {trip.children > 0 && `, ${trip.children} ${trip.children === 1 ? 'child' : 'children'}`}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-white" />
            <span>
              {trip.budget.totalBudget.toLocaleString()} {trip.budget.currency}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
