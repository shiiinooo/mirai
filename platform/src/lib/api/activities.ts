/**
 * Fetch audio for an activity story.
 * 
 * @param activityId - The activity ID
 * @param story - The story text to convert to audio
 * @param tripId - Optional trip ID for cache lookup
 * @returns Audio blob for playback
 */
export async function getActivityAudio(
  activityId: string,
  story: string,
  tripId?: string
): Promise<Blob> {
  const params = new URLSearchParams();
  if (tripId) {
    params.append('trip_id', tripId);
  }
  if (story) {
    params.append('story', story);
  }

  // Use relative path - nginx will proxy to backend
  // For local dev without Docker, use VITE_API_URL if set
  const baseUrl = import.meta.env.VITE_API_URL || '';
  const url = baseUrl ? `${baseUrl}/v1/activities/${activityId}/audio?${params.toString()}` : `/v1/activities/${activityId}/audio?${params.toString()}`;

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'audio/mpeg',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Failed to fetch audio: ${response.status} ${errorText}`);
    }

    return await response.blob();
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('Failed to fetch activity audio');
  }
}

