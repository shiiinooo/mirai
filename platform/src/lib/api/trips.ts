import { supabase } from '../supabase';
import { Trip, TripPlanRequest } from '@/types/trip';
import { apiRequest } from './client';

export async function planTrip(request: TripPlanRequest): Promise<Trip> {
  const trip = await apiRequest<Trip>('/v1/trips/plan', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  await supabase.from('trips').insert({
    id: trip.id,
    destination: trip.destination,
    start_date: trip.startDate,
    end_date: trip.endDate,
    trip_type: trip.tripType,
    trip_data: trip,
  });

  return trip;
}

export async function getTrip(id: string): Promise<Trip | null> {
  const { data, error } = await supabase
    .from('trips')
    .select('trip_data')
    .eq('id', id)
    .maybeSingle();

  if (error) {
    throw new Error(`Failed to fetch trip: ${error.message}`);
  }

  if (!data) {
    return null;
  }

  return data.trip_data as Trip;
}
