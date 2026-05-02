import { useQuery } from '@tanstack/react-query';
import { patientService } from '../services/patientService';

export function usePatients() {
  return useQuery({
    queryKey: ['patients'],
    queryFn: () => patientService.getPatients(),
    refetchInterval: 60000, // Auto-refresh every minute per spec
  });
}

export function usePatientDetail(patientId: string | null) {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: () => patientService.getPatientDetail(patientId!),
    enabled: !!patientId,
  });
}
