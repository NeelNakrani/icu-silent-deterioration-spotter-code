# Frontend-Backend Integration Guide

## Overview
This document describes how the React frontend integrates with the FastAPI backend for the ICU Silent Deterioration Spotter application.

## Backend API Endpoints

The backend runs on `http://localhost:8000` and provides the following endpoints:

### 1. Health Check
- **Endpoint**: `GET /health`
- **Response**: Health status, timestamp, and version
- **Usage**: System health monitoring

### 2. Get Patient List
- **Endpoint**: `GET /patients`
- **Response**: List of all patients with risk information
- **Frontend Hook**: `usePatients()`
- **Auto-refresh**: Every 60 seconds

### 3. Get Patient Brief
- **Endpoint**: `GET /patients/{patient_id}/brief`
- **Response**: Complete SBAR brief with all details
- **Frontend Hook**: `usePatientDetail(patientId)`
- **Usage**: Patient detail view

### 4. Refresh Patient Analysis
- **Endpoint**: `POST /patients/{patient_id}/refresh`
- **Response**: Updated risk information
- **Frontend Hook**: `useRefreshPatient()`
- **Usage**: Manual refresh of patient analysis

### 5. Get Formatted Brief
- **Endpoint**: `GET /patients/{patient_id}/brief/formatted`
- **Response**: Plain text formatted SBAR brief
- **Usage**: Console/debugging

## Frontend Integration

### Configuration

1. **Environment Variables** (`.env`):
```env
VITE_API_BASE_URL=http://localhost:8000
```

2. **API Service** (`src/services/api.service.ts`):
   - Centralized HTTP client
   - Handles all API requests
   - Error handling and response formatting

3. **Patient Service** (`src/services/patientService.ts`):
   - Wraps API calls with business logic
   - Transforms backend responses to frontend types
   - Provides patient-specific operations

### Data Flow

```
Component → Hook → Service → API → Backend
    ↓         ↓        ↓       ↓
  Render ← Cache ← Transform ← Response
```

### Type Transformations

The frontend transforms backend responses to match UI requirements:

#### Patient List Item
Backend → Frontend:
- `risk_level` (string) → `risk_level` (lowercase enum)
- `last_updated` (ISO string) → `last_updated_label` (human-readable)
- `careunit` → `careunit_short` (abbreviated)

#### Patient Brief
Backend → Frontend:
- SBAR sections mapped directly
- Agent summaries → detailed report objects
- Timestamps → human-readable labels
- Risk levels normalized to lowercase

### React Query Integration

All API calls use TanStack Query (React Query) for:
- Automatic caching
- Background refetching
- Loading/error states
- Optimistic updates

#### Example Usage

```typescript
// In a component
import { usePatients, useRefreshPatient } from './hooks';

function Dashboard() {
  const { data: patients, isLoading } = usePatients();
  const { mutate: refresh } = useRefreshPatient();
  
  const handleRefresh = (patientId: string) => {
    refresh(patientId);
  };
  
  // ...
}
```

### Hooks

1. **`usePatients()`**
   - Fetches patient list
   - Auto-refreshes every 60 seconds
   - Returns: `{ data, isLoading, error }`

2. **`usePatientDetail(patientId)`**
   - Fetches patient SBAR brief
   - Enabled only when patientId is provided
   - Returns: `{ data, isLoading, error }`

3. **`useRefreshPatient()`**
   - Mutation hook for refreshing analysis
   - Invalidates queries on success
   - Returns: `{ mutate, isLoading, error }`

## Running the Application

### 1. Start Backend
```bash
cd BE
python -m uvicorn src.api_main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend
```bash
cd FE
npm install
npm run dev
```

### 3. Access Application
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

## Error Handling

The frontend handles errors at multiple levels:

1. **API Service Level**: HTTP errors, network failures
2. **Service Level**: Data transformation errors
3. **Hook Level**: Query/mutation errors
4. **Component Level**: User-facing error messages

## CORS Configuration

The backend is configured to allow all origins in development:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Note**: In production, specify exact origins for security.

## Data Caching Strategy

- **Patient List**: Cached for 1 minute, auto-refreshes every 60 seconds
- **Patient Detail**: Cached until invalidated by refresh
- **Refresh Action**: Invalidates both patient detail and list caches

## Future Enhancements

1. **WebSocket Integration**: Real-time vitals updates
2. **Optimistic Updates**: Immediate UI updates before server confirmation
3. **Offline Support**: Service worker for offline functionality
4. **Error Recovery**: Automatic retry with exponential backoff
5. **Request Cancellation**: Cancel in-flight requests on navigation

## Troubleshooting

### Backend Not Responding
- Check if backend is running on port 8000
- Verify CORS configuration
- Check backend logs for errors

### Data Not Loading
- Check browser console for errors
- Verify API_BASE_URL in `.env`
- Check network tab in DevTools

### Type Mismatches
- Ensure backend response matches `backend-api.types.ts`
- Check transformation functions in `patientService.ts`

## Made with Bob