import { useState, useEffect } from 'react';
import { patientService } from '../services/patientService';
import type { VitalsUpdate } from '../types/icu';

export function useLiveVitals(patientId: string | null) {
  const [vitals, setVitals] = useState<VitalsUpdate | null>(null);

  useEffect(() => {
    if (!patientId) return;

    const unsubscribe = patientService.subscribeToVitals(patientId, (data) => {
      setVitals(data);
    });

    return () => unsubscribe();
  }, [patientId]);

  return vitals;
}
