"""
Module: loader.py
Purpose: Layer 0 - MIMIC-IV data loader and PatientDataObject creator
Layer: 0 (Data Ingestion)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module loads MIMIC-IV data and transforms it into PatientDataObject
instances that can be consumed by Layer 1 agents.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from schemas import (
    PatientDataObject,
    VitalReading,
    LabReading,
    OutputReading,
    MedRecord,
    PendingLab,
    DataQuality
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# MIMIC-IV itemid mappings for vitals
VITAL_ITEMIDS = {
    220045: "Heart Rate",
    220210: "Respiratory Rate",
    220179: "Non Invasive Blood Pressure systolic",
    220180: "Non Invasive Blood Pressure diastolic",
    220277: "O2 saturation pulseoxymetry",
    223761: "Temperature Fahrenheit",
    223762: "Temperature Celsius",
    220052: "Arterial Blood Pressure systolic",
    220051: "Arterial Blood Pressure diastolic",
    220050: "Arterial Blood Pressure mean"
}

# Lab itemids (common ones)
LAB_ITEMIDS = {
    50912: "Creatinine",
    50813: "Lactate",
    51301: "White Blood Cells",
    51222: "Hemoglobin",
    51265: "Platelets",
    50971: "Potassium",
    50983: "Sodium",
    50902: "Chloride",
    50882: "Bicarbonate"
}

# Output itemids
OUTPUT_ITEMIDS = {
    40055: "Urine Out Foley",
    40069: "Urine Out Void",
    40094: "Urine Out Condom Cath",
    40715: "Urine Out Suprapubic",
    226559: "Foley",
    226560: "Void",
    226561: "Condom Cath",
    226584: "Ileostomy",
    226563: "Suprapubic",
    226564: "R Nephrostomy",
    226565: "L Nephrostomy",
    226567: "Straight Cath",
    226557: "R Ureteral Stent",
    226558: "L Ureteral Stent"
}


class DataLoader:
    """
    Loads and processes MIMIC-IV data into PatientDataObject instances.
    """
    
    def __init__(self, data_path: str = "BE/data/raw_data/master_multi_patient_timeline.csv"):
        """
        Initialize the data loader.
        
        Args:
            data_path: Path to the master CSV file
        """
        self.data_path = Path(data_path)
        self.df: Optional[pd.DataFrame] = None
        
    def load_master_data(self) -> None:
        """Load the master dataset into memory."""
        logger.info(f"Loading master data from {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        # Load CSV
        self.df = pd.read_csv(self.data_path)
        
        # Convert datetime columns
        self.df['charttime'] = pd.to_datetime(self.df['charttime'])
        self.df['storetime'] = pd.to_datetime(self.df['storetime'])
        self.df['intime'] = pd.to_datetime(self.df['intime'])
        self.df['outtime'] = pd.to_datetime(self.df['outtime'])
        
        # Sort by patient and time
        self.df = self.df.sort_values(['subject_id', 'charttime']).reset_index(drop=True)
        
        logger.info(f"Loaded {len(self.df)} records")
    
    def create_patient_data_object(
        self,
        patient_id: str,
        window_start: datetime,
        window_end: datetime,
        raw_data: Optional[Dict[str, Any]] = None
    ) -> PatientDataObject:
        """
        Create a PatientDataObject from raw data.
        
        Args:
            patient_id: Subject ID
            window_start: Start of time window
            window_end: End of time window
            raw_data: Optional pre-filtered raw data dict (from emitter)
            
        Returns:
            PatientDataObject instance
        """
        if raw_data is None:
            # Load from master dataset
            if self.df is None:
                self.load_master_data()
            
            patient_df = self.df[
                (self.df['subject_id'] == int(patient_id)) &
                (self.df['charttime'] >= window_start) &
                (self.df['charttime'] < window_end)
            ].copy()
            
            if patient_df.empty:
                raise ValueError(f"No data found for patient {patient_id} in window")
            
            records = patient_df.to_dict('records')
        else:
            # Use provided raw data
            records = raw_data.get('records', [])
            if not records:
                raise ValueError(f"No records in provided raw data")
        
        # Extract patient metadata from first record
        first_record = records[0]
        
        # Initialize PatientDataObject
        pdo = PatientDataObject(
            patient_id=patient_id,
            stay_id=str(first_record.get('stay_id', '')),
            window_start=window_start,
            window_end=window_end,
            gender=first_record.get('gender', 'U'),
            age=int(first_record.get('anchor_age', 0)),
            careunit=first_record.get('first_careunit', 'Unknown'),
            intime=pd.to_datetime(first_record.get('intime')) if first_record.get('intime') else None,
            outtime=pd.to_datetime(first_record.get('outtime')) if first_record.get('outtime') else None
        )
        
        # Process records and categorize
        vitals_list = []
        labs_list = []
        outputs_list = []
        
        for record in records:
            itemid = int(record.get('itemid', 0))
            charttime = pd.to_datetime(record['charttime'])
            valuenum = record.get('valuenum')
            
            if valuenum is None or pd.isna(valuenum):
                continue
            
            valuenum = float(valuenum)
            label = record.get('label', '')
            valueuom = record.get('valueuom', '')
            
            # Categorize by itemid
            if itemid in VITAL_ITEMIDS:
                vitals_list.append(VitalReading(
                    charttime=charttime,
                    label=label,
                    value=valuenum,
                    unit=valueuom,
                    itemid=itemid
                ))
            elif itemid in LAB_ITEMIDS:
                labs_list.append(LabReading(
                    charttime=charttime,
                    label=label,
                    value=valuenum,
                    unit=valueuom,
                    itemid=itemid,
                    flag=None  # Would need additional data for flags
                ))
            elif itemid in OUTPUT_ITEMIDS:
                outputs_list.append(OutputReading(
                    charttime=charttime,
                    value=valuenum,
                    unit=valueuom,
                    itemid=itemid
                ))
        
        # Sort by time
        vitals_list.sort(key=lambda x: x.charttime)
        labs_list.sort(key=lambda x: x.charttime)
        outputs_list.sort(key=lambda x: x.charttime)
        
        pdo.vitals = vitals_list
        pdo.labs = labs_list
        pdo.urine_output = outputs_list
        
        # Calculate data quality
        pdo.data_quality = self._calculate_data_quality(pdo, window_start, window_end)
        
        logger.info(
            f"Created PatientDataObject for {patient_id}: "
            f"{len(vitals_list)} vitals, {len(labs_list)} labs, "
            f"{len(outputs_list)} outputs"
        )
        
        return pdo
    
    def _calculate_data_quality(
        self,
        pdo: PatientDataObject,
        window_start: datetime,
        window_end: datetime
    ) -> DataQuality:
        """
        Calculate data quality metrics for a patient window.
        
        Args:
            pdo: PatientDataObject
            window_start: Start of window
            window_end: End of window
            
        Returns:
            DataQuality object
        """
        # Calculate expected readings (every 30 min for 6 hours = 12 readings per vital)
        window_hours = (window_end - window_start).total_seconds() / 3600
        expected_readings_per_vital = int(window_hours * 2)  # Every 30 min
        
        # Core vitals we expect
        core_vitals = [
            "Heart Rate",
            "Respiratory Rate",
            "Non Invasive Blood Pressure systolic",
            "O2 saturation pulseoxymetry"
        ]
        
        total_expected = expected_readings_per_vital * len(core_vitals)
        
        # Count actual readings by vital type
        vital_counts = {}
        for vital in pdo.vitals:
            vital_counts[vital.label] = vital_counts.get(vital.label, 0) + 1
        
        # Identify missing vitals
        missing_vitals = [v for v in core_vitals if vital_counts.get(v, 0) == 0]
        
        # Calculate data gaps
        data_gaps = []
        if pdo.vitals:
            sorted_vitals = sorted(pdo.vitals, key=lambda x: x.charttime)
            for i in range(len(sorted_vitals) - 1):
                gap_minutes = (sorted_vitals[i+1].charttime - sorted_vitals[i].charttime).total_seconds() / 60
                if gap_minutes > 60:  # Gap larger than 1 hour
                    data_gaps.append(int(gap_minutes))
        
        dq = DataQuality(
            total_expected_readings=total_expected,
            actual_readings=len(pdo.vitals),
            missing_vitals=missing_vitals,
            missing_labs=[],  # Would need more context to determine expected labs
            data_gaps_minutes=data_gaps
        )
        
        dq.calculate_completeness()
        
        return dq
    
    def resample_to_intervals(
        self,
        pdo: PatientDataObject,
        interval_minutes: int = 30
    ) -> PatientDataObject:
        """
        Resample patient data to fixed time intervals.
        
        Args:
            pdo: PatientDataObject
            interval_minutes: Interval size in minutes
            
        Returns:
            Resampled PatientDataObject
        """
        # Create time range
        time_range = pd.date_range(
            start=pdo.window_start,
            end=pdo.window_end,
            freq=f'{interval_minutes}min'
        )
        
        # Resample vitals
        resampled_vitals = []
        vital_types = set(v.label for v in pdo.vitals)
        
        for vital_type in vital_types:
            # Get all readings for this vital type
            vital_readings = [v for v in pdo.vitals if v.label == vital_type]
            if not vital_readings:
                continue
            
            # Create DataFrame for resampling
            df = pd.DataFrame([
                {'charttime': v.charttime, 'value': v.value}
                for v in vital_readings
            ])
            df['charttime'] = pd.to_datetime(df['charttime'])
            df = df.set_index('charttime')
            
            # Resample using forward fill
            resampled = df.resample(f'{interval_minutes}min').mean()
            resampled = resampled.fillna(method='ffill')
            
            # Convert back to VitalReading objects
            for timestamp, row in resampled.iterrows():
                if pd.notna(row['value']):
                    resampled_vitals.append(VitalReading(
                        charttime=timestamp,
                        label=vital_type,
                        value=float(row['value']),
                        unit=vital_readings[0].unit,
                        itemid=vital_readings[0].itemid
                    ))
        
        # Update PDO with resampled vitals
        pdo.vitals = sorted(resampled_vitals, key=lambda x: x.charttime)
        
        logger.info(f"Resampled to {len(pdo.vitals)} readings at {interval_minutes}-min intervals")
        
        return pdo
    
    def extract_rolling_window(
        self,
        patient_id: str,
        at_time: datetime,
        window_hours: int = 6
    ) -> PatientDataObject:
        """
        Extract a rolling window of data for a patient.
        
        Args:
            patient_id: Subject ID
            at_time: Current time point
            window_hours: Size of lookback window in hours
            
        Returns:
            PatientDataObject for the window
        """
        window_start = at_time - timedelta(hours=window_hours)
        window_end = at_time
        
        return self.create_patient_data_object(
            patient_id=patient_id,
            window_start=window_start,
            window_end=window_end
        )
    
    def get_all_patients(self) -> List[str]:
        """
        Get list of all patient IDs in the dataset.
        
        Returns:
            List of patient IDs
        """
        if self.df is None:
            self.load_master_data()
        
        return [str(pid) for pid in self.df['subject_id'].unique()]
    
    def get_patient_time_range(self, patient_id: str) -> tuple[datetime, datetime]:
        """
        Get the time range for a patient's data.
        
        Args:
            patient_id: Subject ID
            
        Returns:
            Tuple of (start_time, end_time)
        """
        if self.df is None:
            self.load_master_data()
        
        patient_df = self.df[self.df['subject_id'] == int(patient_id)]
        
        if patient_df.empty:
            raise ValueError(f"No data found for patient {patient_id}")
        
        return (
            patient_df['charttime'].min(),
            patient_df['charttime'].max()
        )


# Helper functions for integration with emitter

def create_pdo_from_emitter_data(emitter_data: Dict[str, Any]) -> PatientDataObject:
    """
    Create PatientDataObject from emitter output.
    
    Args:
        emitter_data: Dictionary from DataEmitter.emit_patient()
        
    Returns:
        PatientDataObject instance
    """
    loader = DataLoader()
    
    return loader.create_patient_data_object(
        patient_id=emitter_data['patient_id'],
        window_start=pd.to_datetime(emitter_data['window_start']),
        window_end=pd.to_datetime(emitter_data['window_end']),
        raw_data=emitter_data
    )


def process_emitter_batch(batch_data: Dict[str, Any]) -> List[PatientDataObject]:
    """
    Process a batch of patient data from emitter.
    
    Args:
        batch_data: Dictionary from DataEmitter.emit_all_patients()
        
    Returns:
        List of PatientDataObject instances
    """
    loader = DataLoader()
    pdos = []
    
    for patient_id, patient_records in batch_data['patients'].items():
        try:
            pdo = loader.create_patient_data_object(
                patient_id=patient_id,
                window_start=pd.to_datetime(batch_data['window_start']),
                window_end=pd.to_datetime(batch_data['window_end']),
                raw_data={'records': patient_records}
            )
            pdos.append(pdo)
        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {e}")
    
    return pdos


# Example usage and testing
async def test_loader():
    """Test the data loader."""
    from emitter import DataEmitter
    
    # Create emitter and loader
    emitter = DataEmitter(speed_multiplier=100.0)  # Fast for testing
    loader = DataLoader()
    
    # Get patient list
    patients = emitter.get_patient_list()
    logger.info(f"Found {len(patients)} patients")
    
    if patients:
        test_patient = patients[0]['patient_id']
        logger.info(f"Testing loader for patient {test_patient}")
        
        # Get snapshot
        snapshot = emitter.get_snapshot(test_patient, window_hours=6)
        
        # Create PDO
        pdo = create_pdo_from_emitter_data(snapshot)
        
        logger.info(f"Created PDO:")
        logger.info(f"  Patient: {pdo.patient_id}")
        logger.info(f"  Window: {pdo.window_start} to {pdo.window_end}")
        logger.info(f"  Vitals: {len(pdo.vitals)}")
        logger.info(f"  Labs: {len(pdo.labs)}")
        logger.info(f"  Data Quality: {pdo.data_quality.completeness_score:.2%}")
        
        # Test resampling
        resampled_pdo = loader.resample_to_intervals(pdo, interval_minutes=30)
        logger.info(f"  Resampled Vitals: {len(resampled_pdo.vitals)}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_loader())

# Made with Bob
