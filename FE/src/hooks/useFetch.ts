// Custom hook for data fetching
import { useState, useEffect } from 'react';
import type { ApiResponse, ApiError } from '../types/api.types';

interface UseFetchState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

export function useFetch<T>(
  fetchFn: () => Promise<ApiResponse<T>>,
  dependencies: any[] = []
) {
  const [state, setState] = useState<UseFetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      setState({ data: null, loading: true, error: null });

      try {
        const response = await fetchFn();
        if (isMounted) {
          setState({ data: response.data, loading: false, error: null });
        }
      } catch (error) {
        if (isMounted) {
          setState({ data: null, loading: false, error: error as ApiError });
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, dependencies);

  return state;
}

// Made with Bob
