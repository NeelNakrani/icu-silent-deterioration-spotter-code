# Integration Testing Guide

## Prerequisites

Before testing, ensure:
1. Backend is running on `http://localhost:8000`
2. Frontend `.env` file is configured correctly
3. Dependencies are installed (`npm install`)

## Step-by-Step Testing

### 1. Verify Backend is Running

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2026-05-02T09:00:00","version":"1.0.0"}
```

### 2. Test Patient List Endpoint

```bash
# Get patient list
curl http://localhost:8000/patients

# Expected response structure:
# {
#   "patients": [...],
#   "total_count": N,
#   "timestamp": "..."
# }
```

### 3. Test Patient Brief Endpoint

```bash
# Replace {patient_id} with actual patient ID from list
curl http://localhost:8000/patients/{patient_id}/brief

# Expected response includes:
# - patient_id, stay_id
# - risk_level, risk_score
# - situation, background, assessment, recommendation
# - data_quality_score, confidence_level
```

### 4. Test Refresh Endpoint

```bash
# Refresh patient analysis
curl -X POST http://localhost:8000/patients/{patient_id}/refresh

# Expected response:
# {
#   "success": true,
#   "message": "Successfully refreshed...",
#   "patient_id": "...",
#   "risk_level": "...",
#   "risk_score": N
# }
```

## Frontend Testing

### 1. Start Frontend

```bash
cd FE
npm run dev
```

Access at `http://localhost:5173`

### 2. Test Dashboard

**Expected Behavior:**
- Patient list loads automatically
- Risk levels displayed with colors (green/yellow/red)
- Patient cards show basic information
- Auto-refresh every 60 seconds

**Check Browser Console:**
- No CORS errors
- API calls successful (200 status)
- Data transformations working

### 3. Test Patient Detail View

**Steps:**
1. Click on any patient card
2. Detail view should load

**Expected Behavior:**
- SBAR sections displayed
- Risk level and score shown
- Agent reports visible (Trend, Conflict, TimeBomb)
- Data quality metrics displayed

### 4. Test Manual Refresh

**Steps:**
1. Open patient detail view
2. Click refresh button (if available)
3. Wait for analysis to complete

**Expected Behavior:**
- Loading indicator appears
- Data updates after refresh
- No errors in console

## Common Issues and Solutions

### Issue: CORS Error

**Symptom:**
```
Access to fetch at 'http://localhost:8000/patients' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**Solution:**
- Verify backend CORS middleware is configured
- Check `allow_origins` includes frontend URL
- Restart backend after changes

### Issue: 404 Not Found

**Symptom:**
```
GET http://localhost:8000/patients 404 (Not Found)
```

**Solution:**
- Verify backend is running
- Check API endpoint paths match
- Verify `VITE_API_BASE_URL` in `.env`

### Issue: Type Errors

**Symptom:**
```
Property 'X' does not exist on type 'Y'
```

**Solution:**
- Check backend response structure
- Update `backend-api.types.ts` if needed
- Verify transformation functions in `patientService.ts`

### Issue: Empty Patient List

**Symptom:**
- Dashboard loads but shows no patients

**Solution:**
- Check backend has loaded data
- Verify backend logs for errors
- Check browser network tab for response data

## Browser DevTools Checklist

### Network Tab
- [ ] All API calls return 200 status
- [ ] Response data structure matches types
- [ ] No CORS errors
- [ ] Request headers include Content-Type

### Console Tab
- [ ] No error messages
- [ ] TanStack Query logs (if debug enabled)
- [ ] Successful data transformations

### React DevTools
- [ ] Query cache populated
- [ ] Components receiving correct props
- [ ] State updates on data changes

## Performance Testing

### Load Time
- Initial page load: < 2 seconds
- Patient list fetch: < 1 second
- Patient detail fetch: < 1 second
- Refresh operation: < 2 seconds

### Memory Usage
- Monitor for memory leaks
- Check query cache size
- Verify cleanup on unmount

## Integration Test Checklist

- [ ] Backend health check passes
- [ ] Patient list loads successfully
- [ ] Patient detail view works
- [ ] Manual refresh triggers re-analysis
- [ ] Auto-refresh works (60s interval)
- [ ] Error handling displays user-friendly messages
- [ ] Loading states show correctly
- [ ] Data transformations work properly
- [ ] Type safety maintained throughout
- [ ] No console errors or warnings

## Automated Testing (Future)

Consider adding:
- E2E tests with Playwright/Cypress
- API integration tests
- Component tests with React Testing Library
- Mock service worker for offline testing

## Made with Bob