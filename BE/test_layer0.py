"""
Module: test_layer0.py
Purpose: Test script for Layer 0 (emitter + loader) integration
Layer: Testing

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This script tests the integration between the data emitter and loader.
"""

import asyncio
import logging
from datetime import datetime

from emitter import DataEmitter
from loader import DataLoader, create_pdo_from_emitter_data
from schemas import PatientDataObject

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_emitter_basic():
    """Test basic emitter functionality."""
    logger.info("=" * 60)
    logger.info("TEST 1: Basic Emitter Functionality")
    logger.info("=" * 60)
    
    emitter = DataEmitter(speed_multiplier=1000.0)  # Very fast for testing
    
    # Test loading data
    emitter.load_data()
    logger.info(f"✓ Data loaded successfully")
    
    # Test getting patient list
    patients = emitter.get_patient_list()
    logger.info(f"✓ Found {len(patients)} patients")
    
    if patients:
        logger.info(f"  First patient: {patients[0]['patient_id']}")
        logger.info(f"  Age: {patients[0]['age']}, Gender: {patients[0]['gender']}")
        logger.info(f"  Care Unit: {patients[0]['careunit']}")
    
    return patients


async def test_loader_basic():
    """Test basic loader functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Basic Loader Functionality")
    logger.info("=" * 60)
    
    loader = DataLoader()
    
    # Test loading data
    loader.load_master_data()
    logger.info(f"✓ Master data loaded successfully")
    
    # Test getting all patients
    patients = loader.get_all_patients()
    logger.info(f"✓ Found {len(patients)} patients")
    
    return patients


async def test_emitter_snapshot():
    """Test emitter snapshot functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Emitter Snapshot")
    logger.info("=" * 60)
    
    emitter = DataEmitter()
    patients = emitter.get_patient_list()
    
    if not patients:
        logger.error("✗ No patients found")
        return None
    
    test_patient = patients[0]['patient_id']
    logger.info(f"Testing snapshot for patient {test_patient}")
    
    # Get snapshot
    snapshot = emitter.get_snapshot(test_patient, window_hours=6)
    
    logger.info(f"✓ Snapshot retrieved:")
    logger.info(f"  Window: {snapshot['window_start']} to {snapshot['window_end']}")
    logger.info(f"  Records: {snapshot['record_count']}")
    
    return snapshot


async def test_pdo_creation():
    """Test PatientDataObject creation from emitter data."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: PatientDataObject Creation")
    logger.info("=" * 60)
    
    emitter = DataEmitter()
    patients = emitter.get_patient_list()
    
    if not patients:
        logger.error("✗ No patients found")
        return None
    
    test_patient = patients[0]['patient_id']
    snapshot = emitter.get_snapshot(test_patient, window_hours=6)
    
    # Create PDO
    pdo = create_pdo_from_emitter_data(snapshot)
    
    logger.info(f"✓ PatientDataObject created:")
    logger.info(f"  Patient ID: {pdo.patient_id}")
    logger.info(f"  Stay ID: {pdo.stay_id}")
    logger.info(f"  Window: {pdo.window_start} to {pdo.window_end}")
    logger.info(f"  Demographics: {pdo.age}yo {pdo.gender}, {pdo.careunit}")
    logger.info(f"  Vitals: {len(pdo.vitals)} readings")
    logger.info(f"  Labs: {len(pdo.labs)} readings")
    logger.info(f"  Urine Output: {len(pdo.urine_output)} readings")
    
    if pdo.data_quality:
        logger.info(f"  Data Quality: {pdo.data_quality.completeness_score:.1%}")
        logger.info(f"    Expected: {pdo.data_quality.total_expected_readings}")
        logger.info(f"    Actual: {pdo.data_quality.actual_readings}")
        if pdo.data_quality.missing_vitals:
            logger.info(f"    Missing: {', '.join(pdo.data_quality.missing_vitals)}")
    
    return pdo


async def test_resampling():
    """Test data resampling functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Data Resampling")
    logger.info("=" * 60)
    
    emitter = DataEmitter()
    loader = DataLoader()
    patients = emitter.get_patient_list()
    
    if not patients:
        logger.error("✗ No patients found")
        return None
    
    test_patient = patients[0]['patient_id']
    snapshot = emitter.get_snapshot(test_patient, window_hours=6)
    
    # Create PDO
    pdo = create_pdo_from_emitter_data(snapshot)
    logger.info(f"Original vitals: {len(pdo.vitals)} readings")
    
    # Resample to 30-minute intervals
    resampled_pdo = loader.resample_to_intervals(pdo, interval_minutes=30)
    logger.info(f"✓ Resampled to 30-min intervals: {len(resampled_pdo.vitals)} readings")
    
    # Show sample of resampled data
    if resampled_pdo.vitals:
        logger.info(f"  Sample readings:")
        for vital in resampled_pdo.vitals[:5]:
            logger.info(f"    {vital.charttime}: {vital.label} = {vital.value} {vital.unit}")
    
    return resampled_pdo


async def test_streaming():
    """Test streaming data emission."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Streaming Data Emission")
    logger.info("=" * 60)
    
    emitter = DataEmitter(speed_multiplier=1000.0)  # Very fast
    patients = emitter.get_patient_list()
    
    if not patients:
        logger.error("✗ No patients found")
        return
    
    test_patient = patients[0]['patient_id']
    logger.info(f"Streaming data for patient {test_patient}")
    
    window_count = 0
    async for data_window in emitter.emit_patient(test_patient, window_hours=6):
        window_count += 1
        logger.info(f"✓ Window {window_count}:")
        logger.info(f"  Time: {data_window['window_start']} to {data_window['window_end']}")
        logger.info(f"  Records: {data_window['record_count']}")
        
        # Create PDO from this window
        pdo = create_pdo_from_emitter_data(data_window)
        logger.info(f"  PDO: {len(pdo.vitals)} vitals, {len(pdo.labs)} labs")
        
        if window_count >= 3:  # Only test first 3 windows
            logger.info(f"✓ Tested {window_count} windows successfully")
            break


async def test_all_patients_batch():
    """Test batch processing of all patients."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Batch Processing All Patients")
    logger.info("=" * 60)
    
    emitter = DataEmitter(speed_multiplier=10000.0)  # Very fast
    loader = DataLoader()
    
    batch_count = 0
    total_patients = 0
    
    async for batch in emitter.emit_all_patients(window_minutes=30):
        batch_count += 1
        patient_count = batch['patient_count']
        total_patients += patient_count
        
        logger.info(f"✓ Batch {batch_count}:")
        logger.info(f"  Time: {batch['window_start']} to {batch['window_end']}")
        logger.info(f"  Patients: {patient_count}")
        logger.info(f"  Total Records: {batch['record_count']}")
        
        if batch_count >= 2:  # Only test first 2 batches
            logger.info(f"✓ Tested {batch_count} batches with {total_patients} patient windows")
            break


async def run_all_tests():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("LAYER 0 INTEGRATION TESTS")
    logger.info("=" * 80 + "\n")
    
    try:
        # Run tests sequentially
        await test_emitter_basic()
        await test_loader_basic()
        await test_emitter_snapshot()
        await test_pdo_creation()
        await test_resampling()
        await test_streaming()
        await test_all_patients_batch()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())

# Made with Bob
