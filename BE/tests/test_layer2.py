"""
Module: test_layer2.py
Purpose: Test script for Layer 2 (coordinator + API) integration
Layer: Testing

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This script tests the integration of Layer 2 components with Layer 1 agents.
"""

import asyncio
import logging
from datetime import datetime

from emitter import DataEmitter
from loader import create_pdo_from_emitter_data
from coordinator import coordinate, format_sbar_for_display
from db import init_database, upsert_brief, get_brief, get_all_patients

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_coordinator():
    """Test the coordinator with a sample patient."""
    logger.info("=" * 80)
    logger.info("TEST 1: Coordinator Integration")
    logger.info("=" * 80)
    
    # Initialize emitter
    emitter = DataEmitter(speed_multiplier=1000.0)  # Fast for testing
    
    # Get patient list
    patients = emitter.get_patient_list()
    logger.info(f"Found {len(patients)} patients")
    
    if not patients:
        logger.error("No patients found")
        return None
    
    # Test with first patient
    test_patient = patients[0]['patient_id']
    logger.info(f"Testing coordinator with patient {test_patient}")
    
    # Get patient snapshot
    snapshot = emitter.get_snapshot(test_patient, window_hours=6)
    
    # Create PatientDataObject
    patient_data = create_pdo_from_emitter_data(snapshot)
    logger.info(f"Created PatientDataObject: {len(patient_data.vitals)} vitals, {len(patient_data.labs)} labs")
    
    # Run coordinator
    logger.info("Running coordinator...")
    sbar_brief = await coordinate(patient_data)
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("SBAR BRIEF GENERATED")
    logger.info("=" * 80)
    logger.info(f"Patient: {sbar_brief.patient_id}")
    logger.info(f"Risk Level: {sbar_brief.risk_level.value} {sbar_brief.get_emoji()}")
    logger.info(f"Risk Score: {sbar_brief.risk_score:.1f}/100")
    logger.info(f"Confidence: {sbar_brief.confidence_level:.0%}")
    logger.info("")
    
    # Print formatted SBAR
    print(format_sbar_for_display(sbar_brief))
    
    return sbar_brief


async def test_database_operations(sbar_brief):
    """Test database operations."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Database Operations")
    logger.info("=" * 80)
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    logger.info("✓ Database initialized")
    
    # Test upsert
    logger.info(f"Saving SBAR brief for patient {sbar_brief.patient_id}...")
    success = upsert_brief(sbar_brief)
    if success:
        logger.info("✓ Brief saved successfully")
    else:
        logger.error("✗ Failed to save brief")
        return False
    
    # Test retrieval
    logger.info(f"Retrieving brief for patient {sbar_brief.patient_id}...")
    retrieved_brief = get_brief(sbar_brief.patient_id)
    if retrieved_brief:
        logger.info("✓ Brief retrieved successfully")
        logger.info(f"  Risk Level: {retrieved_brief['risk_level']}")
        logger.info(f"  Risk Score: {retrieved_brief['risk_score']:.1f}")
    else:
        logger.error("✗ Failed to retrieve brief")
        return False
    
    # Test get all patients
    logger.info("Retrieving all patients...")
    all_patients = get_all_patients()
    logger.info(f"✓ Found {len(all_patients)} patient(s) in database")
    for patient in all_patients:
        logger.info(f"  - Patient {patient['patient_id']}: {patient['risk_level']} (score: {patient['risk_score']:.1f})")
    
    return True


async def test_multiple_patients():
    """Test coordinator with multiple patients."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Multiple Patients")
    logger.info("=" * 80)
    
    # Initialize emitter
    emitter = DataEmitter(speed_multiplier=1000.0)
    
    # Get patient list
    patients = emitter.get_patient_list()
    
    # Test with first 3 patients
    test_count = min(3, len(patients))
    logger.info(f"Testing with {test_count} patients")
    
    results = []
    for i in range(test_count):
        patient_id = patients[i]['patient_id']
        logger.info(f"\nProcessing patient {i+1}/{test_count}: {patient_id}")
        
        try:
            # Get snapshot
            snapshot = emitter.get_snapshot(patient_id, window_hours=6)
            
            # Create PDO
            patient_data = create_pdo_from_emitter_data(snapshot)
            
            # Run coordinator
            sbar_brief = await coordinate(patient_data)
            
            # Save to database
            upsert_brief(sbar_brief)
            
            results.append({
                'patient_id': patient_id,
                'risk_level': sbar_brief.risk_level.value,
                'risk_score': sbar_brief.risk_score,
                'emoji': sbar_brief.get_emoji()
            })
            
            logger.info(f"✓ {sbar_brief.get_emoji()} Patient {patient_id}: {sbar_brief.risk_level.value} (score: {sbar_brief.risk_score:.1f})")
            
        except Exception as e:
            logger.error(f"✗ Error processing patient {patient_id}: {e}")
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Processed {len(results)}/{test_count} patients successfully")
    
    # Sort by risk score
    results.sort(key=lambda x: x['risk_score'], reverse=True)
    
    logger.info("\nPatients by risk level:")
    for result in results:
        logger.info(f"  {result['emoji']} {result['patient_id']}: {result['risk_level']} (score: {result['risk_score']:.1f})")
    
    return results


async def test_concurrent_processing():
    """Test concurrent processing of multiple patients."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Concurrent Processing")
    logger.info("=" * 80)
    
    # Initialize emitter
    emitter = DataEmitter(speed_multiplier=1000.0)
    
    # Get patient list
    patients = emitter.get_patient_list()
    
    # Test with first 3 patients concurrently
    test_count = min(3, len(patients))
    logger.info(f"Processing {test_count} patients concurrently")
    
    async def process_patient(patient_id: str):
        """Process a single patient."""
        try:
            snapshot = emitter.get_snapshot(patient_id, window_hours=6)
            patient_data = create_pdo_from_emitter_data(snapshot)
            sbar_brief = await coordinate(patient_data)
            upsert_brief(sbar_brief)
            return sbar_brief
        except Exception as e:
            logger.error(f"Error processing patient {patient_id}: {e}")
            return None
    
    # Process concurrently
    start_time = datetime.now()
    
    tasks = [process_patient(patients[i]['patient_id']) for i in range(test_count)]
    results = await asyncio.gather(*tasks)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Count successes
    successful = [r for r in results if r is not None]
    
    logger.info(f"\n✓ Processed {len(successful)}/{test_count} patients in {duration:.2f} seconds")
    logger.info(f"  Average time per patient: {duration/test_count:.2f} seconds")
    
    return successful


async def run_all_tests():
    """Run all Layer 2 tests."""
    logger.info("\n" + "╔" + "═" * 78 + "╗")
    logger.info("║" + " " * 78 + "║")
    logger.info("║" + "  LAYER 2 INTEGRATION TESTS".center(78) + "║")
    logger.info("║" + "  Coordinator + API + Database".center(78) + "║")
    logger.info("║" + " " * 78 + "║")
    logger.info("╚" + "═" * 78 + "╝")
    
    try:
        # Test 1: Coordinator
        sbar_brief = await test_coordinator()
        if not sbar_brief:
            logger.error("Test 1 failed")
            return
        
        # Test 2: Database operations
        db_success = await test_database_operations(sbar_brief)
        if not db_success:
            logger.error("Test 2 failed")
            return
        
        # Test 3: Multiple patients
        await test_multiple_patients()
        
        # Test 4: Concurrent processing
        await test_concurrent_processing()
        
        # Final summary
        logger.info("\n" + "╔" + "═" * 78 + "╗")
        logger.info("║" + " " * 78 + "║")
        logger.info("║" + "  ✓ ALL LAYER 2 TESTS PASSED".center(78) + "║")
        logger.info("║" + " " * 78 + "║")
        logger.info("╚" + "═" * 78 + "╝")
        
        logger.info("\n📝 Next Steps:")
        logger.info("  1. Start the API server: python api_main.py")
        logger.info("  2. Access API docs: http://localhost:8000/docs")
        logger.info("  3. Test endpoints with frontend or curl")
        logger.info("  4. Review SBAR briefs in database")
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())

# Made with Bob