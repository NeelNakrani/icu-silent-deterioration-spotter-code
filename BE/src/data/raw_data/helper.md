### Agent Field Mapping & Trend Logic

#### 1. Trend Agent (Rate-of-Change)
*   **Fields**: `Heart Rate`, `Respiratory Rate`, `Systolic BP`, `SpO2`, `Temperature`.
*   **Logic**: Uses a 6-point window to calculate the slope. Rapidly increasing HR + falling BP = Early Sepsis/Shock warning.

#### 2. Lab-Vitals Conflict Agent (Pattern Recognition)
*   **Fields**: `Creatinine` (Lab) vs `Urine Output` (Vitals) for AKI; `Lactate` (Lab) vs `MAP/HR` (Vitals) for Shock.
*   **Logic**: Flags if vitals look 'normal' but underlying labs are deteriorating (Compensated Shock).

#### 3. Time Bomb Agent (Predictive Ops)
*   **Fields**: `charttime`, `order_subtype` (from `poe`), `medication` (from `prescriptions`).
*   **Logic**: Scans the next 3 hours for critical medication stops or missing labs.




The field breakdown for master_multi_patient_timeline.csv. This file is the primary data source for the Bob Agents' simulation.

Master Dataset Field Guide
Field	Description	Agent Relevance
subject_id	Unique patient identifier.	Used to group time-series data per individual.
stay_id	Unique identifier for the specific ICU admission.	Context for when a patient moves units.
charttime	The timestamp when the vital was recorded.	Critical for the Trend Agent to calculate velocity.
label	Name of the vital sign (e.g., Heart Rate, SpO2).	Key filter for physiological analysis.
valuenum	The numeric value of the vital sign.	The raw data point used for threshold checks.
gender / anchor_age	Patient demographics.	Used to adjust risk scores (e.g., age-adjusted HR targets).
first_careunit	The specific ICU type (e.g., MICU, SICU).	Context for the Time Bomb Agent (unit-specific workflows).
intime / outtime	Admission and discharge timestamps.	Defines the simulation boundaries for each patient.
This structure allows the agents to track a patient's trajectory from the moment they enter the ICU until they leave, calculating risks in real-time based on the charttime sequence.