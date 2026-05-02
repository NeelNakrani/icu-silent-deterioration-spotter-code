import { useMutation, useQueryClient } from '@tanstack/react-query';
import { patientService } from '../services/patientService';
import type { RefreshResponse } from '../types/backend-api.types';

/**
 * Hook to refresh patient analysis
 * Invalidates queries to trigger refetch after successful refresh
 */
export function useRefreshPatient() {
  const queryClient = useQueryClient();

  return useMutation<RefreshResponse, Error, string>({
    mutationFn: (patientId: string) => patientService.refreshAnalysis(patientId),
    onSuccess: (data, patientId) => {
      // Invalidate and refetch patient queries
      queryClient.invalidateQueries({ queryKey: ['patient', patientId] });
      queryClient.invalidateQueries({ queryKey: ['patients'] });
      
      console.log(`Successfully refreshed analysis for patient ${patientId}`);
    },
    onError: (error, patientId) => {
      console.error(`Failed to refresh analysis for patient ${patientId}:`, error);
    },
  });
}

// Made with Bob