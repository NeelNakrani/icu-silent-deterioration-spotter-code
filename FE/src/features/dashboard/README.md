# Dashboard Component Documentation

## Overview

The Dashboard component is the primary patient list view for the ICU Silent Deterioration Spotter system. It provides a comprehensive overview of all patients in the ICU with real-time monitoring, risk assessment, and filtering capabilities.

## File Location

[`FE/src/features/dashboard/Dashboard.tsx`](./Dashboard.tsx)

## Component Architecture

### Main Components

#### 1. **Dashboard** (Main Component)
The root component that orchestrates the entire dashboard view.

**Props:**
```typescript
interface DashboardProps {
  patients: PatientSummary[];  // Array of patient data
  onOpen: (patient: PatientSummary) => void;  // Callback when patient card is clicked
  density?: string;  // UI density setting ("dense" | "regular")
}
```

**State Management:**
- `unit`: Current unit filter ("All Units" | "MICU" | "SICU")
- `currentPage`: Current pagination page (0-indexed)
- `riskFilter`: Active risk level filter ("all" | "red" | "yellow" | "green")

**Features:**
- Unit-based filtering
- Risk level filtering
- Pagination (12 patients per page)
- Automatic page reset on filter changes

---

#### 2. **Header**
Top navigation bar with branding, unit switcher, and live status indicator.

**Props:**
```typescript
interface HeaderProps {
  unit: string;
  setUnit: (unit: string) => void;
  refresh?: boolean;  // Enable auto-refresh countdown
  density?: string;
}
```

**Features:**
- **Branding**: "Sentinel ICU" logo and version
- **Unit Switcher**: Segmented control for All Units/MICU/SICU
- **Live Status**: Animated pulse indicator with 60s countdown
- **Actions**: Filter button (placeholder)

**Auto-refresh:**
- Displays countdown timer (60s cycle)
- Visual pulse animation on status indicator
- Shows "GET /patients · Xs" format

---

#### 3. **StatStrip**
Statistics bar showing census data and risk level distribution.

**Props:**
```typescript
interface StatStripProps {
  patients: PatientSummary[];
  riskFilter: RiskLevel | "all";
  onRiskFilterChange: (filter: RiskLevel | "all") => void;
}
```

**Statistics Displayed:**
1. **Census**: Total active beds
2. **Red**: Critical patients (clickable filter)
3. **Yellow**: Watch patients (clickable filter)
4. **Green**: Stable patients (clickable filter)
5. **Open flags**: Total flags across cohort
6. **Agent runs/hr**: Performance metric (mock: 142, p50 4.2s)

**Interactive Features:**
- Click Red/Yellow/Green to filter patients by risk level
- Active filter shows highlighted border and background
- Hover effects on clickable stats
- Toggle behavior (click again to reset to "all")

---

#### 4. **PatientCards**
Grid layout displaying individual patient cards.

**Props:**
```typescript
interface SubComponentProps {
  patients: PatientSummary[];
  onOpen: (patient: PatientSummary) => void;
}
```

**Card Layout:**
Each card displays:

**Header Section:**
- Unit and demographics (e.g., "MICU · 65M")
- Patient ID (subject_id format)
- Primary diagnosis
- Risk pill with score and delta

**Flags Section:**
- Color-coded clinical flags
- "No active flags" message when empty
- Flag tone mapping:
  - Red: shock, arrest, anuria, vasopres, rising
  - Amber: lactate, trop, plat, pf, gap, hgb
  - Neutral: all others

**Vitals Section:**
- HR (Heart Rate) with trend
- MAP (Mean Arterial Pressure) with trend
- SpO₂ (Oxygen Saturation) with trend
- RR (Respiratory Rate)

**Metadata Section:**
- Agent badges (trend/conflict/timebomb counts)
- Last updated timestamp

**Visual Design:**
- Left border color matches risk level
- Red risk patients get enhanced shadow
- Hover effects for interactivity
- Responsive grid (min 320px columns)

---

#### 5. **PaginationControls**
Bottom navigation for page switching.

**Props:**
```typescript
interface PaginationControlsProps {
  onPrev?: () => void;  // Previous page handler (undefined if on first page)
  onNext?: () => void;  // Next page handler (undefined if on last page)
  pageInfo?: string;    // Page display (e.g., "1 / 3")
}
```

**Features:**
- Previous/Next arrow buttons
- Disabled state when at boundaries
- Current page indicator
- SVG icons for arrows

---

## Data Flow

```
Dashboard
  ├─ Receives patients[] prop
  ├─ Filters by unit → unitPatients
  ├─ Filters by risk level → filteredPatients
  ├─ Paginates → visiblePatients
  │
  ├─ Header (unit switching)
  ├─ StatStrip (shows unitPatients stats, handles risk filtering)
  ├─ PatientCards (displays visiblePatients)
  └─ PaginationControls (page navigation)
```

## Filtering Logic

### Unit Filtering
```typescript
// Filter by selected unit
let filteredPatients = patients.filter(p => 
  unit === "All Units" || p.careunit_short === unit
);
```

### Risk Level Filtering
```typescript
// Then filter by risk level if active
if (riskFilter !== "all") {
  filteredPatients = filteredPatients.filter(p => 
    p.risk_level === riskFilter
  );
}
```

### Pagination
```typescript
const pageSize = 12;
const pageCount = Math.ceil(filteredPatients.length / pageSize);
const visiblePatients = filteredPatients.slice(
  currentPage * pageSize, 
  (currentPage + 1) * pageSize
);
```

## Styling System

### CSS Variables Used

**Colors:**
- `--surface-0`, `--surface-1`, `--surface-2`: Background layers
- `--ink-1`, `--ink-2`, `--ink-3`, `--ink-4`: Text hierarchy
- `--rule`, `--rule-soft`: Border colors
- `--accent`: Brand accent color
- `--ok`: Success/live indicator color
- `--chip-bg`: Chip background
- `--risk-high-fg`, `--risk-med-fg`, `--risk-low-fg`: Risk level colors

**Typography:**
- `--mono`: Monospace font family

### Button Styles

**btnGhost:**
```typescript
{
  padding: "5px 11px",
  border: "1px solid var(--rule)",
  background: "var(--surface-1)",
  color: "var(--ink-2)",
  borderRadius: 7,
  fontSize: 11.5,
  fontWeight: 500,
  cursor: "pointer"
}
```

## Helper Functions

### `riskVar(level: RiskLevel)`
Maps risk levels to CSS variable suffixes:
- `"red"` → `"high"`
- `"yellow"` → `"med"`
- `"green"` → `"low"`

### `flagTone(flag: string)`
Determines flag color based on content:
- Returns `"red"` for critical flags (shock, arrest, etc.)
- Returns `"amber"` for warning flags (lactate, troponin, etc.)
- Returns `"neutral"` for others

## Integration

### Required Types
From [`types/icu.ts`](../../types/icu.ts):
- `PatientSummary`
- `RiskLevel`
- `Vitals`
- `AgentCounts`
- `TrendDirection`

### Required Components
From [`components/index.ts`](../../components/index.ts):
- `RiskPill`
- `Chip`
- `VitalCell`
- `AgentBadge`

### Usage in App
From [`App.tsx`](../../App.tsx):
```typescript
import Dashboard from './features/dashboard/Dashboard';

<Dashboard
  patients={patients}
  onOpen={openPatient}
  density={t.density}
/>
```

## Performance Considerations

1. **Pagination**: Only renders 12 patients at a time to maintain performance
2. **Filtering**: Filters are applied before pagination to reduce render load
3. **Memoization**: Consider using `React.memo` for PatientCards if performance issues arise
4. **Virtual Scrolling**: Could be added for very large patient lists

## Accessibility

- Semantic HTML structure
- ARIA labels on pagination buttons
- Keyboard navigation support through native button elements
- Color contrast meets WCAG standards
- Screen reader friendly text labels

## Future Enhancements

1. **Search/Filter Panel**: Implement the "Filters" button functionality
2. **Sort Options**: Add sorting by risk score, last updated, etc.
3. **View Modes**: Add table and compact list views
4. **Export**: Add CSV/PDF export functionality
5. **Bulk Actions**: Select multiple patients for batch operations
6. **Real-time Updates**: WebSocket integration for live data
7. **Customizable Page Size**: Allow users to change items per page
8. **Saved Filters**: Persist user filter preferences

## Testing Recommendations

### Unit Tests
- Filter logic (unit and risk level)
- Pagination calculations
- Flag tone mapping
- Risk variable mapping

### Integration Tests
- Patient card click navigation
- Filter interactions
- Pagination navigation
- Unit switching

### E2E Tests
- Full dashboard workflow
- Filter combinations
- Performance with large datasets
- Responsive behavior

## Related Documentation

- [DASHBOARD_RESPONSIVE_DESIGN.md](../../documents/DASHBOARD_RESPONSIVE_DESIGN.md)
- [Patient Detail Component](../patientDetail/PatientDetail.tsx)
- [API Specification](../../../api-spec.yaml)
- [Frontend Guidelines](../../FE-Guidelines.md)