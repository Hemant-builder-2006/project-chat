import { useState, useEffect } from 'react';
import api from '../services/api';
import { Channel } from '../types';

interface UseChannelsResult {
  channels: Channel[];
  isLoading: boolean;
  error: string | null;
}

/**
 * useChannels Hook
 * 
 * Fetches channels for a specific group
 * 
 * Parameters:
 * - groupId: ID of the group to fetch channels for (null if no group selected)
 * 
 * Dependency on groupId:
 * - Only fetches if groupId is not null
 * - Re-fetches when groupId changes
 * - Clears channels when groupId becomes null
 * 
 * This prevents unnecessary API calls and ensures channels
 * are always in sync with the selected group
 */
export const useChannels = (groupId: string | null): UseChannelsResult => {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Don't fetch if no group is selected
    if (!groupId) {
      setChannels([]);
      setIsLoading(false);
      return;
    }

    let isMounted = true;

    const fetchChannels = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.get<Channel[]>(`/groups/${groupId}/channels`);
        
        if (isMounted) {
          setChannels(response.data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to fetch channels');
          console.error('Error fetching channels:', err);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchChannels();

    return () => {
      isMounted = false;
    };
  }, [groupId]); // Re-run when groupId changes

  return { channels, isLoading, error };
};
