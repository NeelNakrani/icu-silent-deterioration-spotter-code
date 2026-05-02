import React from 'react';
import Dashboard from './features/dashboard/Dashboard';
import PatientDetail from './features/patientDetail/PatientDetail';
import { TweaksPanel, TweakSection, TweakRadio, TweakButton } from './components';
import { usePatients, usePatientDetail, useTweaks } from './hooks';
import type { PatientSummary } from './types/icu';

const TWEAK_DEFAULTS = {
  "theme": "light",
  "agentVisual": "tinted",
  "density": "regular"
};


export default function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [screen, setScreen] = React.useState<"dashboard" | "detail">("dashboard");
  const [selectedPatientId, setSelectedPatientId] = React.useState<string | null>(null);

  // TanStack Queries
  const { data: patients = [], isLoading: isLoadingList } = usePatients();
  const { data: detail, isLoading: isLoadingDetail } = usePatientDetail(selectedPatientId);

  React.useEffect(() => {
    document.documentElement.dataset.theme = t.theme;
  }, [t.theme]);

  const openPatient = (p: PatientSummary) => {
    setSelectedPatientId(p.patient_id);
    setScreen("detail");
  };
  
  const back = () => {
    setScreen("dashboard");
    setSelectedPatientId(null);
  };

  const isLoading = isLoadingList || isLoadingDetail;

  if (isLoading && screen === "dashboard" && patients.length === 0) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh', fontFamily: 'var(--mono)', color: 'var(--ink-3)' }}>
        Loading ICU Dashboard...
      </div>
    );
  }

  return (
    <>
      {screen === "dashboard"
        ? <div data-screen-label="01 Patient List Dashboard">
            <Dashboard
              patients={patients}
              onOpen={openPatient}
              density={t.density}
            />
          </div>
        : detail && (
          <div data-screen-label="02 SBAR+ Patient Detail">
            <PatientDetail 
              patient={detail}
              onBack={back} 
              agentVisual={t.agentVisual} 
            />
          </div>
        )
      }

      {isLoading && (
        <div style={{
          position: 'fixed', top: 12, left: '50%', transform: 'translateX(-50%)',
          background: 'var(--ink-1)', color: 'var(--surface-1)', padding: '4px 12px',
          borderRadius: 99, fontSize: 10, fontFamily: 'var(--mono)', zIndex: 9999
        }}>
          REFRESHING...
        </div>
      )}

      <TweaksPanel title="Tweaks">
        <TweakSection label="Theme" />
        <TweakRadio label="Mode" value={t.theme}
          options={["light", "dark"]}
          onChange={(v) => setTweak("theme", v)} />

        <TweakSection label="Detail · agent visual" />
        <TweakRadio label="Style" value={t.agentVisual}
          options={[
            { value: "tinted", label: "Tinted" },
            { value: "neutral", label: "Neutral" },
          ]}
          onChange={(v) => setTweak("agentVisual", v)} />

        <TweakSection label="Navigation" />
        <TweakButton label={screen === "dashboard" ? "Open detail (B-12)" : "Back to dashboard"}
          onClick={() => {
            if (screen === "dashboard" && patients.length > 0) openPatient(patients[0]);
            else back();
          }} />
      </TweaksPanel>
    </>
  );
}
