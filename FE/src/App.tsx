import React from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useParams } from 'react-router-dom';
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

function DashboardPage() {
  const navigate = useNavigate();
  const { data: patients = [], isLoading } = usePatients();

  const openPatient = (p: PatientSummary) => {
    navigate(`/patient-detail/${p.patient_id}`);
  };

  if (isLoading && patients.length === 0) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh', fontFamily: 'var(--mono)', color: 'var(--ink-3)' }}>
        Loading ICU Dashboard...
      </div>
    );
  }

  return (
    <div data-screen-label="01 Patient List Dashboard">
      <Dashboard
        patients={patients}
        onOpen={openPatient}
        density="regular"
      />
    </div>
  );
}

function PatientDetailPage() {
  const navigate = useNavigate();
  const { patientId } = useParams<{ patientId: string }>();
  const { data: detail, isLoading } = usePatientDetail(patientId || null);

  const back = () => {
    navigate('/');
  };

  if (isLoading || !detail) {
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh', fontFamily: 'var(--mono)', color: 'var(--ink-3)' }}>
        Loading patient details...
      </div>
    );
  }

  return (
    <div data-screen-label="02 SBAR+ Patient Detail">
      <PatientDetail
        patient={detail}
        onBack={back}
        agentVisual="tinted"
      />
    </div>
  );
}

function AppContent() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const navigate = useNavigate();
  const { data: patients = [] } = usePatients();

  React.useEffect(() => {
    document.documentElement.dataset.theme = t.theme;
  }, [t.theme]);

  return (
    <>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/patient-detail/:patientId" element={<PatientDetailPage />} />
      </Routes>

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
        <TweakButton label="Toggle View"
          onClick={() => {
            if (window.location.pathname === '/') {
              if (patients.length > 0) navigate(`/patient-detail/${patients[0].patient_id}`);
            } else {
              navigate('/');
            }
          }} />
      </TweaksPanel>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
