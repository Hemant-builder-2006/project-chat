import { useState, useEffect } from 'react';
import api from '../services/api';
import { Group } from '../types';

interface UseGroupsResult {
  groups: Group[];
  isLoading: boolean;
  error: string | null;
}

/**
 * useGroups Hook
 * 
 * Fetches the list of groups the user belongs to
 * 
 * Returns:
 * - groups: Array of Group objects
 * - isLoading: Boolean indicating if the fetch is in progress
 * - error: Error message if the fetch failed, null otherwise
 * 
 * How it manages state:
 * 1. Initializes with empty groups array and loading=true
 * 2. Fetches data from API on mount
 * 3. Updates groups and sets loading=false on success
 * 4. Sets error message and loading=false on failure
 * 5. Cleanup function prevents state updates after unmount
 */
export const useGroups = (): UseGroupsResult => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchGroups = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await api.get<Group[]>('/groups');
        
        if (isMounted) {
          setGroups(response.data);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.response?.data?.detail || 'Failed to fetch groups');
          console.error('Error fetching groups:', err);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchGroups();

    // Cleanup function to prevent state updates after unmount
    return () => {
      isMounted = false;
    };
  }, []);

  return { groups, isLoading, error };
};
