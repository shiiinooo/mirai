import { supabase } from '../supabase';
import { Trip, TripPlanRequest } from '@/types/trip';
import { apiRequest } from './client';

export async function planTrip(request: TripPlanRequest): Promise<Trip> {
  const trip = await apiRequest<Trip>('/v1/trips/plan', {
    method: 'POST',
    body: JSON.stringify(request),
  });

  // Only save to Supabase if it's configured
  if (supabase) {
    const { error: insertError } = await supabase.from('trips').insert({
      id: trip.id,
      destination: trip.destination,
      start_date: trip.startDate,
      end_date: trip.endDate,
      adults: trip.adults,
      children: trip.children,
      trip_data: trip,
    });

    if (insertError) {
      console.error('Failed to save trip to Supabase:', insertError);
      // Don't throw - trip was successfully generated, just failed to save to DB
    }
  } else {
    console.log('Supabase not configured - trip not saved to database');
  }

  return trip;
}

export async function getTrip(id: string): Promise<Trip | null> {
  if (!supabase) {
    throw new Error('Supabase not configured - cannot retrieve saved trips');
  }

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
