import type { PatientSummary, PatientDetailData, VitalsUpdate } from '../types/icu';
import { PATIENTS, PATIENT_DETAIL } from '../data/mockPatients';

/**
 * Service to handle patient-related API calls.
 * Currently uses mock data but is structured for easy replacement with fetch/axios.
 */
export const patientService = {
  /**
   * Fetch a list of all patients for the dashboard.
   */
  async getPatients(): Promise<PatientSummary[]> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // In a real app:
    // const response = await fetch('/api/patients');
    // return response.json();
    
    return PATIENTS;
  },

  /**
   * Fetch full SBAR+ details for a specific patient.
   */
  async getPatientDetail(patientId: string): Promise<PatientDetailData> {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 600));
    
    // In a real app:
    // const response = await fetch(`/api/patients/${patientId}/detail`);
    // return response.json();
    
    // For now, we always return the same detail but mapped to the requested ID if it matches
    if (patientId === PATIENT_DETAIL.patient_id) {
      return PATIENT_DETAIL;
    }
    
    // Fallback: search in list or return a default
    const summary = PATIENTS.find(p => p.patient_id === patientId);
    if (summary) {
       return { ...PATIENT_DETAIL, ...summary };
    }
    
    return PATIENT_DETAIL;
  },

  /**
   * Refresh agent analysis (coordinator synthesis).
   */
  async refreshAnalysis(patientId: string): Promise<void> {
     await new Promise(resolve => setTimeout(resolve, 1500));
     console.log(`Refreshed analysis for ${patientId}`);
  },

  /**
   * Simulate a WebSocket subscription for real-time vitals.
   * In a real app, this would use new WebSocket() or a library like socket.io.
   */
  subscribeToVitals(patientId: string, onUpdate: (vitals: VitalsUpdate) => void): () => void {
    console.log(`Subscribing to live vitals for ${patientId}`);
    
    // Simulate incoming data every 2 seconds
    const interval = setInterval(() => {
      const update = {
        hr: Math.floor(70 + Math.random() * 20),
        map: Math.floor(80 + Math.random() * 15),
        spo2: Math.floor(94 + Math.random() * 5),
        rr: Math.floor(14 + Math.random() * 6),
        timestamp: new Date().toISOString(),
      };
      onUpdate(update);
    }, 2000);

    // Return unsubscribe function
    return () => {
      console.log(`Unsubscribing from vitals for ${patientId}`);
      clearInterval(interval);
    };
  }
};
