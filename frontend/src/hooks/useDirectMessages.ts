import { useState, useEffect } from 'react';
import api from '../services/api';
import { DM } from '../types';

interface UseDirectMessagesResult {
  directMessages: DM[];
  isLoading: boolean;
  error: string | null;
}

/**
 * useDirectMessages Hook
 * 
 * Fetches the list of direct message conversations
 * 
 * Similar to useGroups, but for DM conversations
 */
export const useDirectMessages = (): UseDirectMessagesResult => {
  const [directMessages, setDirectMessages] = useState<DM[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchDirectMessages = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.get<DM[]>('/dms');
        
        if (isMounted) {
          setDirectMessages(response.data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to fetch direct messages');
          console.error('Error fetching direct messages:', err);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchDirectMessages();

    return () => {
      isMounted = false;
    };
  }, []);

  return { directMessages, isLoading, error };
};
