"""
Module: emitter.py
Purpose: Data emitter/simulator for testing - streams patient data in real-time
Layer: 0 (Data Ingestion)

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module simulates real-time data streaming from the MIMIC-IV dataset,
allowing the system to be tested without requiring live ICU data feeds.
"""

import asyncio
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, AsyncGenerator, List, Dict, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataEmitter:
    """
    Emits patient data in real-time simulation mode.
    
    Reads from master_multi_patient_timeline.csv and streams data
    as if it were happening in real-time, respecting the original
    charttime intervals.
    """
    
    def __init__(
        self,
        data_path: Optional[str] = None,
        speed_multiplier: float = 1.0,
        loop_data: bool = False
    ):
        """
        Initialize the data emitter.
        
        Args:
            data_path: Path to the master CSV file (defaults to data/raw_data/master_multi_patient_timeline.csv)
            speed_multiplier: Speed up/slow down time (1.0 = real-time, 2.0 = 2x speed)
            loop_data: Whether to loop the data when reaching the end
        """
        if data_path is None:
            # Default to path relative to this module
            module_dir = Path(__file__).parent
            data_path = module_dir / "data" / "raw_data" / "master_multi_patient_timeline.csv"
        self.data_path = Path(data_path)
        self.speed_multiplier = speed_multiplier
        self.loop_data = loop_data
        self.df: Optional[pd.DataFrame] = None
        self.patients: List[str] = []
        self.current_time: Optional[datetime] = None
        
    def load_data(self) -> None:
        """Load the master dataset into memory."""
        logger.info(f"Loading data from {self.data_path}")
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"Data file not found: {self.data_path}")
        
        # Load CSV
        self.df = pd.read_csv(self.data_path)
        
        # Convert charttime to datetime
        self.df['charttime'] = pd.to_datetime(self.df['charttime'])
        self.df['intime'] = pd.to_datetime(self.df['intime'])
        self.df['outtime'] = pd.to_datetime(self.df['outtime'])
        
        # Sort by charttime
        self.df = self.df.sort_values('charttime').reset_index(drop=True)
        
        # Get unique patients
        self.patients = self.df['subject_id'].unique().tolist()
        
        # Set initial time to first charttime
        self.current_time = self.df['charttime'].min()
        
        logger.info(f"Loaded {len(self.df)} records for {len(self.patients)} patients")
        logger.info(f"Time range: {self.current_time} to {self.df['charttime'].max()}")
    
    async def emit_all_patients(
        self,
        window_minutes: int = 30
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Emit data for all patients in time-windowed batches.
        
        Args:
            window_minutes: Size of time window to emit at once (default: 30 minutes)
            
        Yields:
            Dictionary containing timestamp and patient data for that window
        """
        if self.df is None:
            self.load_data()
        
        logger.info("Starting data emission for all patients")
        
        start_time = self.df['charttime'].min()
        end_time = self.df['charttime'].max()
        current_window_start = start_time
        
        while current_window_start < end_time:
            current_window_end = current_window_start + timedelta(minutes=window_minutes)
            
            # Get all records in this time window
            window_data = self.df[
                (self.df['charttime'] >= current_window_start) &
                (self.df['charttime'] < current_window_end)
            ]
            
            if not window_data.empty:
                # Group by patient
                patient_data = {}
                for patient_id in window_data['subject_id'].unique():
                    patient_records = window_data[
                        window_data['subject_id'] == patient_id
                    ].to_dict('records')
                    patient_data[str(patient_id)] = patient_records
                
                yield {
                    'timestamp': current_window_start.isoformat(),
                    'window_start': current_window_start.isoformat(),
                    'window_end': current_window_end.isoformat(),
                    'patient_count': len(patient_data),
                    'record_count': len(window_data),
                    'patients': patient_data
                }
                
                logger.info(
                    f"Emitted window {current_window_start} - {current_window_end}: "
                    f"{len(patient_data)} patients, {len(window_data)} records"
                )
            
            # Sleep to simulate real-time (adjusted by speed multiplier)
            sleep_time = (window_minutes * 60) / self.speed_multiplier
            await asyncio.sleep(sleep_time)
            
            # Move to next window
            current_window_start = current_window_end
        
        logger.info("Data emission complete")
    
    async def emit_patient(
        self,
        patient_id: str,
        window_hours: int = 6
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Emit data for a specific patient in a rolling window.
        
        Args:
            patient_id: Subject ID to emit data for
            window_hours: Size of rolling window in hours
            
        Yields:
            Dictionary containing patient data for the current window
        """
        if self.df is None:
            self.load_data()
        
        # Filter to specific patient
        patient_df = self.df[self.df['subject_id'] == int(patient_id)].copy()
        
        if patient_df.empty:
            logger.warning(f"No data found for patient {patient_id}")
            return
        
        logger.info(f"Starting data emission for patient {patient_id}")
        
        start_time = patient_df['charttime'].min()
        end_time = patient_df['charttime'].max()
        current_time = start_time
        
        while current_time < end_time:
            window_start = current_time
            window_end = current_time + timedelta(hours=window_hours)
            
            # Get data in current window
            window_data = patient_df[
                (patient_df['charttime'] >= window_start) &
                (patient_df['charttime'] < window_end)
            ]
            
            if not window_data.empty:
                # Get patient metadata from first record
                first_record = window_data.iloc[0]
                
                yield {
                    'patient_id': patient_id,
                    'stay_id': str(first_record['stay_id']),
                    'window_start': window_start.isoformat(),
                    'window_end': window_end.isoformat(),
                    'gender': first_record['gender'],
                    'age': int(first_record['anchor_age']),
                    'careunit': first_record['first_careunit'],
                    'intime': first_record['intime'].isoformat(),
                    'outtime': first_record['outtime'].isoformat(),
                    'record_count': len(window_data),
                    'records': window_data.to_dict('records')
                }
                
                logger.info(
                    f"Patient {patient_id}: Emitted window {window_start} - {window_end} "
                    f"({len(window_data)} records)"
                )
            
            # Move forward by 30 minutes (sliding window)
            current_time += timedelta(minutes=30)
            
            # Sleep to simulate real-time
            sleep_time = (30 * 60) / self.speed_multiplier
            await asyncio.sleep(sleep_time)
        
        logger.info(f"Data emission complete for patient {patient_id}")
    
    def get_patient_list(self) -> List[Dict[str, Any]]:
        """
        Get list of all patients with basic metadata.
        
        Returns:
            List of dictionaries with patient information
        """
        if self.df is None:
            self.load_data()
        
        patient_list = []
        for patient_id in self.patients:
            patient_data = self.df[self.df['subject_id'] == patient_id].iloc[0]
            patient_list.append({
                'patient_id': str(patient_id),
                'stay_id': str(patient_data['stay_id']),
                'gender': patient_data['gender'],
                'age': int(patient_data['anchor_age']),
                'careunit': patient_data['first_careunit'],
                'intime': patient_data['intime'].isoformat(),
                'outtime': patient_data['outtime'].isoformat(),
                'record_count': len(self.df[self.df['subject_id'] == patient_id])
            })
        
        return patient_list
    
    def get_snapshot(
        self,
        patient_id: str,
        at_time: Optional[datetime] = None,
        window_hours: int = 6
    ) -> Dict[str, Any]:
        """
        Get a snapshot of patient data at a specific time.
        
        Args:
            patient_id: Subject ID
            at_time: Time to get snapshot at (default: latest available)
            window_hours: Size of lookback window
            
        Returns:
            Dictionary with patient data snapshot
        """
        if self.df is None:
            self.load_data()
        
        patient_df = self.df[self.df['subject_id'] == int(patient_id)].copy()
        
        if patient_df.empty:
            return {}
        
        if at_time is None:
            at_time = patient_df['charttime'].max()
        
        window_start = at_time - timedelta(hours=window_hours)
        
        window_data = patient_df[
            (patient_df['charttime'] >= window_start) &
            (patient_df['charttime'] <= at_time)
        ]
        
        if window_data.empty:
            return {}
        
        first_record = window_data.iloc[0]
        
        return {
            'patient_id': patient_id,
            'stay_id': str(first_record['stay_id']),
            'snapshot_time': at_time.isoformat(),
            'window_start': window_start.isoformat(),
            'window_end': at_time.isoformat(),
            'gender': first_record['gender'],
            'age': int(first_record['anchor_age']),
            'careunit': first_record['first_careunit'],
            'intime': first_record['intime'].isoformat(),
            'outtime': first_record['outtime'].isoformat(),
            'record_count': len(window_data),
            'records': window_data.to_dict('records')
        }


# Example usage and testing
async def test_emitter():
    """Test the data emitter with sample output."""
    emitter = DataEmitter(speed_multiplier=10.0)  # 10x speed for testing
    
    # Get patient list
    patients = emitter.get_patient_list()
    logger.info(f"Found {len(patients)} patients")
    
    if patients:
        # Test single patient emission
        test_patient = patients[0]['patient_id']
        logger.info(f"Testing emission for patient {test_patient}")
        
        count = 0
        async for data_window in emitter.emit_patient(test_patient, window_hours=6):
            logger.info(f"Received window: {data_window['window_start']} to {data_window['window_end']}")
            logger.info(f"  Records: {data_window['record_count']}")
            count += 1
            if count >= 3:  # Only test first 3 windows
                break


if __name__ == "__main__":
    # Run test
    asyncio.run(test_emitter())

# Made with Bob
