import { apiRequest } from './client';

export interface Airport {
  code: string;
  name: string;
  city: string;
  country: string;
  displayName: string;
}

export async function searchAirports(query: string): Promise<Airport[]> {
  if (!query || query.length < 2) {
    return [];
  }

  try {
    const airports = await apiRequest<Airport[]>(
      `/v1/airports/search?q=${encodeURIComponent(query)}`
    );
    return airports;
  } catch (error) {
    console.error('Failed to search airports:', error);
    return [];
  }
}

