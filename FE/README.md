# ICU Silent Deterioration Spotter - Frontend

React + TypeScript + Vite application for monitoring ICU patients and detecting silent deterioration.

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## Backend Integration

This frontend integrates with the FastAPI backend. See [`INTEGRATION_GUIDE.md`](./INTEGRATION_GUIDE.md) for detailed integration documentation.

### API Configuration

The frontend connects to the backend via environment variables:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Key Features

- **Patient Dashboard**: Real-time patient list with risk levels
- **SBAR+ Detail View**: Comprehensive patient analysis
- **Agent Reasoning**: Trend, Conflict, and TimeBomb agent outputs
- **Auto-refresh**: Patient data refreshes every 60 seconds
- **Manual Refresh**: Trigger re-analysis for specific patients

## Project Structure

```
src/
├── components/       # Reusable UI components
├── features/         # Feature-specific components
│   ├── dashboard/    # Patient list dashboard
│   └── patientDetail/# Patient detail view
├── hooks/            # Custom React hooks
│   ├── usePatients.ts        # Fetch patient list
│   ├── usePatientDetail.ts   # Fetch patient details
│   └── useRefreshPatient.ts  # Refresh patient analysis
├── services/         # API integration layer
│   ├── api.service.ts        # HTTP client
│   └── patientService.ts     # Patient API calls
├── types/            # TypeScript type definitions
│   ├── icu.ts                # Frontend types
│   └── backend-api.types.ts  # Backend API types
└── utils/            # Utility functions
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server with HMR

# Build
npm run build        # Build for production
npm run preview      # Preview production build

# Linting
npm run lint         # Run ESLint
```

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - Component library

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/patients` | GET | Fetch patient list |
| `/patients/{id}/brief` | GET | Fetch patient SBAR brief |
| `/patients/{id}/refresh` | POST | Refresh patient analysis |
| `/health` | GET | Health check |

## Development

### Adding New Features

1. Create types in `src/types/`
2. Add API calls in `src/services/`
3. Create hooks in `src/hooks/`
4. Build components in `src/components/` or `src/features/`

### Type Safety

All API responses are typed using TypeScript. Backend types are defined in `backend-api.types.ts` and transformed to frontend types in the service layer.

### State Management

- **Server State**: TanStack Query (React Query)
- **Local State**: React hooks (useState, useReducer)
- **URL State**: React Router (when applicable)

## Troubleshooting

### Backend Connection Issues

1. Verify backend is running: `http://localhost:8000/health`
2. Check CORS configuration in backend
3. Verify `VITE_API_BASE_URL` in `.env`

### Build Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf .vite
```

### Type Errors

Ensure backend response types match `backend-api.types.ts`. Update transformation functions in `patientService.ts` if needed.

## Production Build

```bash
# Build for production
npm run build

# Output will be in dist/
# Serve with any static file server
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_APP_NAME` | `ICU Silent Deterioration Spotter` | Application name |
| `VITE_APP_VERSION` | `1.0.0` | Application version |
| `VITE_ENABLE_DEBUG` | `false` | Enable debug mode |

## Contributing

1. Follow TypeScript best practices
2. Use existing hooks and services
3. Add types for all new features
4. Test with real backend before committing

## License

IBM Hackathon 2026

## Made with Bob
