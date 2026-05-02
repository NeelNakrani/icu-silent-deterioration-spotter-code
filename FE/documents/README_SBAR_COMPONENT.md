# SBARBrief Component - "The Money View"

## Overview
The SBARBrief component is the Right Panel of the ICU Silent Deterioration Spotter. It presents critical patient deterioration insights in a "Police Report" format—designed to be understood by non-clinical judges in under 60 seconds.

## Component Location
- **Main Component**: `frontend/src/features/components/SBARBrief.tsx`
- **Types**: `frontend/src/types/sbar.types.ts`
- **Demo**: `frontend/src/features/components/SBARBriefDemo.tsx`

## Features

### 1. The "60-Second" Header
- **Risk Badge**: Full-width status bar (RED/YELLOW/GREEN) with color-coded urgency
- **Vital Metadata**: Patient ID and ICU Stay # in high-legibility monospace font
- **Data Freshness**: Timestamp showing the exact data window being analyzed

### 2. The Inference Engine (3 Critical Questions)
- **Trend Agent**: "What's Changing?" - Bold sentence explaining the trend
- **Lab-Conflict Agent**: "Concerning Combination" - Explains dangerous data combinations
- **Time Bomb Agent**: "Next 2 Hours" - High-priority box with urgent attention items

### 3. The Evidence Tray
- Collapsible section showing all raw data points
- Proves AI isn't hallucinating—it's calculating from real measurements
- Smooth transition animation

## Design Principles

### Pre-Attentive Attributes
The component uses visual urgency cues that communicate before reading:
- **RED Risk**: Red glow effect on "Next 2 Hours" box, thick red borders
- **YELLOW Risk**: Yellow glow effect, warning-colored borders
- **GREEN Risk**: Green glow effect, success-colored borders

### No Medical Jargon
All medical terms are paired with plain language explanations:
- "HR: 112 bpm (High Heart Rate > 110)"
- "SpO2: 91% on 4L O2 (Low oxygen saturation)"
- "Tachypnea" → "Respiratory Rate: 28 breaths/min (normal 12-20)"

### Visual Hierarchy
Font weights and sizes guide the eye:
1. **Risk Level** (largest, boldest)
2. **Primary Concern** (Time Bomb section)
3. **Supporting Data** (Trend and Conflict sections)
4. **Evidence** (collapsible, detailed)

## Usage

### Basic Usage
```tsx
import { SBARBrief } from './features/components';
import type { SBARBrief as SBARBriefType } from './types';

const patientData: SBARBriefType = {
  risk: "RED",
  patientId: "P-101",
  stayCount: "Day 4",
  window: "Last 6h as of 08:15",
  trend: "Progressive respiratory fatigue...",
  conflict: "Lactate is rising despite...",
  timeBomb: "High risk of intubation...",
  reasoning: ["HR: 112bpm", "SpO2: 91%", ...]
};

<SBARBrief data={patientData} />
```

### Demo Component
To see the component in action with mock data:
```tsx
import { SBARBriefDemo } from './features/components';

<SBARBriefDemo />
```

### Integration with Dashboard
```tsx
// In Dashboard.tsx
import { SBARBrief } from '../components';

export default function Dashboard() {
  return (
    <div className="grid grid-cols-2 gap-6">
      <div>{/* Left panel content */}</div>
      <div className="h-screen">
        <SBARBrief data={patientData} />
      </div>
    </div>
  );
}
```

## Responsive Design
- Optimized for laptop screens (no horizontal scrolling)
- Uses Tailwind CSS v4 with custom theme variables
- Flexible height with internal scrolling for long content

## Theme Variables Used
From `frontend/src/index.css`:
- `--color-bg-panel`: Panel background
- `--color-bg-elevated`: Elevated sections
- `--color-bg-main`: Main background
- `--color-text-primary`: Primary text
- `--color-text-secondary`: Secondary text
- `--color-text-muted`: Muted text
- `--color-critical`: Red risk indicator
- `--color-warning`: Yellow risk indicator
- `--color-success`: Green risk indicator
- `--color-highlight`: Accent highlights
- `--color-border-subtle`: Subtle borders

## Mock Data Structure
```typescript
{
  risk: "RED" | "YELLOW" | "GREEN",
  patientId: string,
  stayCount: string,
  window: string,
  trend: string,
  conflict: string,
  timeBomb: string,
  reasoning: string[]
}
```

## Testing the Component

### Run the Demo
1. Start the development server:
   ```bash
   cd frontend
   npm run dev
   ```

2. Import and use `SBARBriefDemo` in your app to see it in action

### Visual Testing Checklist
- [ ] RED risk shows red glow on Time Bomb section
- [ ] YELLOW risk shows yellow glow
- [ ] GREEN risk shows green glow
- [ ] Evidence Tray expands/collapses smoothly
- [ ] No horizontal scrolling on laptop screens
- [ ] All text is readable in dark mode
- [ ] Monospace fonts render correctly for Patient ID

## Future Enhancements
- Real-time data updates
- Historical trend graphs
- Export to PDF functionality
- Multi-patient comparison view
- Alert sound notifications for critical changes