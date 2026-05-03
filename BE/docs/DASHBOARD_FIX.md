# Dashboard Risk Level Distribution Fix

## Issue Description

The dashboard was showing all 100 patients as "stable" (GREEN risk level) despite the data analysis indicating that:
- 37 patients (37%) have abnormal vital signs at some point
- 63 patients (63%) have only stable vital signs
- 205 warning events are distributed across the 37 at-risk patients

## Root Cause

In [`BE/src/api_main.py`](../src/api_main.py), the `/patients` endpoint was defaulting all patients without cached SBAR briefs to `RiskLevel.GREEN` with a risk score of `0.0`.

```python
# OLD CODE (lines 156-167)
else:
    # No brief yet, show as unknown
    patient_item = PatientListItem(
        patient_id=patient_id,
        stay_id=patient['stay_id'],
        risk_level=RiskLevel.GREEN,  # ❌ Always defaulting to GREEN
        risk_score=0.0,
        ...
    )
```

Since the system hadn't generated SBAR briefs for any patients yet (briefs are generated on-demand), all 100 patients were showing as GREEN.

## Solution

Added a new function `calculate_risk_from_data()` that analyzes the raw patient data (specifically the `warning` column) to determine initial risk levels:

### Risk Calculation Logic

```python
def calculate_risk_from_data(patient_id: str) -> tuple[RiskLevel, float]:
    """
    Calculate risk level from raw patient data when no brief is available.
    
    Logic:
    - Count warnings in patient's data
    - Calculate warning percentage
    - Assign risk level:
      * GREEN (0.0): No warnings - stable
      * YELLOW (45-55): < 1% warnings - watch closely  
      * RED (75-100): ≥ 1% warnings - critical attention
    """
```

### Risk Level Thresholds

| Warning Count | Warning % | Risk Level | Score Range | Status |
|--------------|-----------|------------|-------------|---------|
| 0 | 0% | 🟢 GREEN | 0.0 | Stable |
| 1+ | < 1% | 🟡 YELLOW | 45-55 | Watch closely |
| Many | ≥ 1% | 🔴 RED | 75-100 | Critical attention |

## Expected Results

After the fix, the dashboard should show:
- **63 patients** with GREEN (stable) - those with no warnings
- **37 patients** with YELLOW or RED - those with warning events

The exact distribution between YELLOW and RED will depend on the frequency of warnings for each patient.

## Data Analysis Reference

From [`DATA_ANALYSIS_SUMMARY.md`](../src/data/raw_data/DATA_ANALYSIS_SUMMARY.md):
- Total patients: 100
- Patients with warnings: 37 (37%)
- Patients without warnings: 63 (63%)
- Total warning events: 205 (0.35% of all readings)

## Files Modified

1. **BE/src/api_main.py**
   - Added `calculate_risk_from_data()` function (lines 104-154)
   - Modified `/patients` endpoint to use the new function (line 158)

## Testing

To verify the fix:

1. Start the backend server:
   ```bash
   cd BE
   python src/api_main.py
   ```

2. Check the `/patients` endpoint:
   ```bash
   curl http://localhost:8000/patients
   ```

3. Verify the dashboard shows distributed risk levels:
   - Census: 100 active beds
   - Red: X critical patients
   - Yellow: Y watch patients  
   - Green: Z stable patients
   - Where X + Y + Z = 100

## Future Improvements

1. **More sophisticated risk scoring**: Consider trend severity, conflict types, and timebomb urgency
2. **Caching**: Cache calculated risks to avoid recalculating on every request
3. **Real-time updates**: Update risk levels as new data arrives via WebSocket
4. **Historical tracking**: Track risk level changes over time for each patient