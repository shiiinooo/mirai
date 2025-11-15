/**
 * Fetch audio for a key phrase pronunciation.
 * 
 * @param phrase - The phrase text to pronounce
 * @param language - Optional language code for voice selection
 * @returns Audio blob for playback
 */
export async function getPhraseAudio(
    phrase: string,
    language?: string
  ): Promise<Blob> {
    const params = new URLSearchParams();
    params.append('phrase', phrase);
    if (language) {
      params.append('language', language);
    }
  
    // Use relative path - nginx will proxy to backend
    // For local dev without Docker, use VITE_API_URL if set
    const baseUrl = import.meta.env.VITE_API_URL || '';
    const url = baseUrl 
      ? `${baseUrl}/v1/phrases/audio?${params.toString()}` 
      : `/v1/phrases/audio?${params.toString()}`;
  
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
      throw new Error('Failed to fetch phrase audio');
    }
  }
  
  