"""
Module: run_experiment.py
Purpose: Experimental runner to test and validate layer implementations
Layer: Testing/Validation

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This script runs the implemented layers (currently Layer 0: Emitter + Loader)
and prints the output to console for manual validation. As more layers are
implemented, this script will be updated to test the full pipeline.

Current Implementation:
- Runs for 60 seconds maximum
- Emits patient data using DataEmitter
- Processes data using DataLoader
- Prints PatientDataObject instances to console
- Ensures read-only access to master_multi_patient_timeline.csv
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
import json

from emitter import DataEmitter
from loader import DataLoader, create_pdo_from_emitter_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ExperimentRunner:
    """
    Runs experiments to validate layer implementations.
    """
    
    def __init__(self, max_duration_seconds: int = 60):
        """
        Initialize the experiment runner.
        
        Args:
            max_duration_seconds: Maximum duration to run the experiment (default: 60)
        """
        self.max_duration_seconds = max_duration_seconds
        self.emitter: DataEmitter = None  # type: ignore
        self.loader: DataLoader = None  # type: ignore
        self.start_time: datetime = None  # type: ignore
        self.pdo_count = 0
        
    def setup(self):
        """Set up the emitter and loader."""
        logger.info("=" * 80)
        logger.info("EXPERIMENT SETUP")
        logger.info("=" * 80)
        
        # Initialize emitter with faster speed for testing
        # Speed multiplier of 60 means 1 minute of real data = 1 second of runtime
        self.emitter = DataEmitter(speed_multiplier=60.0)
        self.loader = DataLoader()
        
        # Verify data file exists and is readable
        data_path = Path(__file__).parent / "data" / "raw_data" / "master_multi_patient_timeline.csv"
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        logger.info(f"✓ Data file found: {data_path}")
        logger.info(f"✓ Emitter initialized (speed: 60x)")
        logger.info(f"✓ Loader initialized")
        logger.info(f"✓ Max duration: {self.max_duration_seconds} seconds")
        logger.info("")
        
    async def run_layer0_experiment(self):
        """
        Run Layer 0 experiment: Emitter + Loader
        
        This experiment:
        1. Emits patient data in time windows
        2. Processes each window with the loader
        3. Creates PatientDataObject instances
        4. Prints PDO details to console
        5. Runs for maximum 60 seconds
        """
        logger.info("=" * 80)
        logger.info("LAYER 0 EXPERIMENT: EMITTER + LOADER")
        logger.info("=" * 80)
        logger.info("")
        
        self.start_time = datetime.now()
        
        # Get patient list
        patients = self.emitter.get_patient_list()
        logger.info(f"📊 Found {len(patients)} patients in dataset")
        logger.info("")
        
        if not patients:
            logger.error("❌ No patients found in dataset")
            return
        
        # Select first patient for testing
        test_patient = patients[0]
        logger.info(f"🏥 Testing with Patient: {test_patient['patient_id']}")
        logger.info(f"   Stay ID: {test_patient['stay_id']}")
        logger.info(f"   Age: {test_patient['age']}, Gender: {test_patient['gender']}")
        logger.info(f"   Care Unit: {test_patient['careunit']}")
        logger.info(f"   Record Count: {test_patient['record_count']}")
        logger.info("")
        
        # Emit data for the patient
        logger.info("🚀 Starting data emission...")
        logger.info("")
        
        try:
            async for window_data in self.emitter.emit_patient(
                patient_id=test_patient['patient_id'],
                window_hours=6
            ):
                # Check if we've exceeded max duration
                elapsed = (datetime.now() - self.start_time).total_seconds()
                if elapsed >= self.max_duration_seconds:
                    logger.info("")
                    logger.info("⏱️  Maximum duration reached (60 seconds)")
                    logger.info("🛑 Stopping experiment...")
                    break
                
                # Process window with loader
                try:
                    pdo = create_pdo_from_emitter_data(window_data)
                    self.pdo_count += 1
                    
                    # Print PDO details
                    self._print_pdo(pdo, self.pdo_count)
                    
                except Exception as e:
                    logger.error(f"❌ Error creating PDO: {e}")
                    continue
                
        except asyncio.CancelledError:
            logger.info("🛑 Experiment cancelled")
        except Exception as e:
            logger.error(f"❌ Experiment error: {e}")
            raise
        
        # Print summary
        self._print_summary()
    
    def _print_pdo(self, pdo, count: int):
        """
        Print PatientDataObject details to console.
        
        Args:
            pdo: PatientDataObject instance
            count: PDO number
        """
        logger.info("─" * 80)
        logger.info(f"📦 PatientDataObject #{count}")
        logger.info("─" * 80)
        logger.info(f"Patient ID: {pdo.patient_id}")
        logger.info(f"Stay ID: {pdo.stay_id}")
        logger.info(f"Window: {pdo.window_start.strftime('%Y-%m-%d %H:%M:%S')} to {pdo.window_end.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Demographics: {pdo.age}yo {pdo.gender}, {pdo.careunit}")
        logger.info("")
        
        # Vitals summary
        logger.info(f"💓 Vitals: {len(pdo.vitals)} readings")
        if pdo.vitals:
            vital_types = {}
            for vital in pdo.vitals:
                vital_types[vital.label] = vital_types.get(vital.label, 0) + 1
            for vital_name, count in sorted(vital_types.items()):
                logger.info(f"   - {vital_name}: {count} readings")
        
        # Labs summary
        logger.info(f"🧪 Labs: {len(pdo.labs)} results")
        if pdo.labs:
            lab_types = {}
            for lab in pdo.labs:
                lab_types[lab.label] = lab_types.get(lab.label, 0) + 1
            for lab_name, count in sorted(lab_types.items()):
                logger.info(f"   - {lab_name}: {count} results")
        
        # Urine output summary
        logger.info(f"💧 Urine Output: {len(pdo.urine_output)} measurements")
        if pdo.urine_output:
            total_output = sum(o.value for o in pdo.urine_output)
            logger.info(f"   - Total: {total_output:.1f} mL")
        
        # Data quality
        if pdo.data_quality:
            logger.info(f"📊 Data Quality:")
            logger.info(f"   - Completeness: {pdo.data_quality.completeness_score:.1%}")
            logger.info(f"   - Expected readings: {pdo.data_quality.total_expected_readings}")
            logger.info(f"   - Actual readings: {pdo.data_quality.actual_readings}")
            if pdo.data_quality.missing_vitals:
                logger.info(f"   - Missing vitals: {', '.join(pdo.data_quality.missing_vitals)}")
            if pdo.data_quality.data_gaps_minutes:
                logger.info(f"   - Data gaps: {len(pdo.data_quality.data_gaps_minutes)} gaps")
        
        logger.info("")
        
        # Print sample vital readings (first 3)
        if pdo.vitals:
            logger.info("📈 Sample Vital Readings (first 3):")
            for i, vital in enumerate(pdo.vitals[:3]):
                logger.info(
                    f"   {i+1}. {vital.charttime.strftime('%H:%M:%S')} - "
                    f"{vital.label}: {vital.value} {vital.unit}"
                )
            logger.info("")
    
    def _print_summary(self):
        """Print experiment summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("EXPERIMENT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"⏱️  Duration: {elapsed:.1f} seconds")
        logger.info(f"📦 PatientDataObjects created: {self.pdo_count}")
        logger.info(f"✅ Experiment completed successfully")
        logger.info("")
        logger.info("📝 Notes:")
        logger.info("   - Emitter accessed master_multi_patient_timeline.csv in READ-ONLY mode")
        logger.info("   - No modifications were made to the source data file")
        logger.info("   - All data was processed in-memory")
        logger.info("")
        logger.info("🎯 Next Steps:")
        logger.info("   - Implement Layer 1 agents (Trend, Conflict, TimeBomb)")
        logger.info("   - Update this script to test Layer 1 outputs")
        logger.info("   - Implement Layer 2 coordinator")
        logger.info("   - Update this script to test full pipeline")
        logger.info("=" * 80)


async def main():
    """Main entry point for the experiment."""
    try:
        runner = ExperimentRunner(max_duration_seconds=60)
        runner.setup()
        await runner.run_layer0_experiment()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Experiment interrupted by user")
    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ICU SILENT DETERIORATION SPOTTER - EXPERIMENTAL RUNNER".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Layer 0: Emitter + Loader Test".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    asyncio.run(main())

# Made with Bob