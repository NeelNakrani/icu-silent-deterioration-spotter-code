# Frontend Folder Structure

This document describes the organization of the React + TypeScript + Tailwind CSS frontend application.

## Directory Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.svg
│   └── icons.svg
│
├── src/
│   ├── assets/            # Images, fonts, and other static files
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   │
│   ├── config/            # Application configuration
│   │   └── index.ts       # Environment variables and app config
│   │
│   ├── context/           # React Context providers
│   │   └── index.ts
│   │
│   ├── hooks/             # Custom React hooks
│   │   ├── index.ts
│   │   ├── useDebounce.ts
│   │   ├── useFetch.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── layouts/           # Layout components (MainLayout, AuthLayout, etc.)
│   │   └── index.ts
│   │
│   ├── lib/               # Third-party library configurations
│   │   └── index.ts
│   │
│   ├── pages/             # Page components
│   │   └── index.ts
│   │
│   ├── routes/            # Route configuration
│   │   └── index.tsx
│   │
│   ├── services/          # API services and external integrations
│   │   ├── index.ts
│   │   └── api.service.ts
│   │
│   ├── store/             # State management (Redux/Zustand/Context)
│   │   └── index.ts
│   │
│   ├── styles/            # Global styles and Tailwind CSS
│   │   └── index.css
│   │
│   ├── types/             # TypeScript type definitions
│   │   ├── index.ts
│   │   ├── api.types.ts
│   │   └── models.types.ts
│   │
│   ├── utils/             # Utility functions
│   │   ├── index.ts
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── validation.ts
│   │
│   ├── App.tsx            # Main App component
│   ├── App.css            # App-specific styles
│   ├── main.tsx           # Application entry point
│   └── index.css          # Global CSS imports
│
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── eslint.config.js       # ESLint configuration
├── index.html             # HTML entry point
├── package.json           # Dependencies and scripts
├── postcss.config.js      # PostCSS configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
├── tsconfig.app.json      # TypeScript app-specific config
├── tsconfig.node.json     # TypeScript Node-specific config
└── vite.config.ts         # Vite configuration
```

## Folder Descriptions

### `/src/assets`
Static files like images, fonts, and icons used throughout the application.

### `/src/config`
Application-wide configuration including environment variables and feature flags.

### `/src/context`
React Context providers for global state management (authentication, theme, etc.).

### `/src/hooks`
Custom React hooks for reusable logic:
- `useDebounce`: Debounce values
- `useFetch`: Data fetching with loading/error states
- `useLocalStorage`: localStorage management

### `/src/layouts`
Layout components that wrap pages (e.g., MainLayout, AuthLayout, DashboardLayout).

### `/src/lib`
Third-party library configurations and wrappers.

### `/src/pages`
Page-level components representing different routes in the application.

### `/src/routes`
Route configuration and navigation setup.

### `/src/services`
API services and external integrations:
- `api.service.ts`: HTTP client for API requests

### `/src/store`
State management setup (Redux, Zustand, or Context API).

### `/src/styles`
Global styles and Tailwind CSS configuration.

### `/src/types`
TypeScript type definitions:
- `api.types.ts`: API-related types
- `models.types.ts`: Data model types

### `/src/utils`
Utility functions:
- `constants.ts`: Application constants
- `helpers.ts`: Helper functions (formatting, debounce, throttle)
- `validation.ts`: Validation functions

## Configuration Files

- **tailwind.config.js**: Tailwind CSS customization (colors, spacing, fonts)
- **postcss.config.js**: PostCSS plugins configuration
- **vite.config.ts**: Vite build tool configuration
- **tsconfig.json**: TypeScript compiler options
- **.env.example**: Template for environment variables

## Getting Started

1. Copy `.env.example` to `.env` and configure your environment variables
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`
4. Build for production: `npm run build`

## Notes

- This structure follows React best practices and is scalable for large applications
- Components should be added in a separate `/src/components` directory when needed
- Each major feature can have its own subdirectory structure within relevant folders