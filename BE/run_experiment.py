"""
Module: run_experiment.py
Purpose: Experimental runner to test and validate layer implementations
Layer: Testing/Validation

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This script runs the implemented layers and prints the output to console for
manual validation.

Supported Layers:
- Layer 0: Emitter + Loader (data ingestion)
- Layer 1: Trend Agent + Conflict Agent + TimeBomb Agent (includes Layer 0)

Usage:
    python run_experiment.py --layer 0  # Test Layer 0 only
    python run_experiment.py --layer 1  # Test Layer 1 (includes Layer 0)
    python run_experiment.py            # Default: Layer 0
"""

import asyncio
import logging
import argparse
from datetime import datetime
from pathlib import Path
import json

from emitter import DataEmitter
from loader import DataLoader, create_pdo_from_emitter_data
from trend_agent import analyze_trends
from conflict_agent import detect_conflicts
from timebomb_agent import identify_timebombs

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
    
    def __init__(self, layer: int = 0, max_duration_seconds: int = 60):
        """
        Initialize the experiment runner.
        
        Args:
            layer: Layer to test (0 or 1)
            max_duration_seconds: Maximum duration to run the experiment (default: 60)
        """
        self.layer = layer
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
        logger.info(f"✓ Testing Layer: {self.layer}")
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
        self._print_layer0_summary()
    
    async def run_layer1_experiment(self):
        """
        Run Layer 1 experiment: Layer 0 + All Three Agents
        
        This experiment:
        1. Runs Layer 0 (Emitter + Loader)
        2. Passes PatientDataObject to all three agents concurrently
        3. Prints agent reports to console
        4. Runs for maximum 60 seconds
        """
        logger.info("=" * 80)
        logger.info("LAYER 1 EXPERIMENT: EMITTER + LOADER + AGENTS")
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
        logger.info("🚀 Starting data emission and agent analysis...")
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
                    
                    # Print PDO details (brief version)
                    self._print_pdo_brief(pdo, self.pdo_count)
                    
                    # Run all three agents concurrently
                    logger.info("🤖 Running Layer 1 agents concurrently...")
                    trend_report, conflict_report, timebomb_report = await asyncio.gather(
                        analyze_trends(pdo),
                        detect_conflicts(pdo),
                        identify_timebombs(pdo)
                    )
                    
                    # Print agent reports
                    self._print_agent_reports(trend_report, conflict_report, timebomb_report)
                    
                except Exception as e:
                    logger.error(f"❌ Error processing window: {e}")
                    continue
                
        except asyncio.CancelledError:
            logger.info("🛑 Experiment cancelled")
        except Exception as e:
            logger.error(f"❌ Experiment error: {e}")
            raise
        
        # Print summary
        self._print_layer1_summary()
    
    def _print_pdo(self, pdo, count: int):
        """
        Print PatientDataObject details to console (full version).
        
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
    
    def _print_pdo_brief(self, pdo, count: int):
        """
        Print PatientDataObject details to console (brief version for Layer 1).
        
        Args:
            pdo: PatientDataObject instance
            count: PDO number
        """
        logger.info("─" * 80)
        logger.info(f"📦 PatientDataObject #{count}")
        logger.info("─" * 80)
        logger.info(f"Patient: {pdo.patient_id} | Window: {pdo.window_start.strftime('%H:%M')} - {pdo.window_end.strftime('%H:%M')}")
        logger.info(f"Data: {len(pdo.vitals)} vitals, {len(pdo.labs)} labs, {len(pdo.urine_output)} outputs")
        logger.info("")
    
    def _print_agent_reports(self, trend_report, conflict_report, timebomb_report):
        """
        Print agent reports to console.
        
        Args:
            trend_report: TrendReport from trend agent
            conflict_report: ConflictReport from conflict agent
            timebomb_report: TimeBombReport from timebomb agent
        """
        # Trend Agent Report
        logger.info("┌" + "─" * 78 + "┐")
        logger.info("│" + " 📈 TREND AGENT REPORT".ljust(78) + "│")
        logger.info("├" + "─" * 78 + "┤")
        logger.info(f"│ Overall Concern: {trend_report.overall_concern}/3".ljust(79) + "│")
        logger.info(f"│ Trends Analyzed: {len(trend_report.trends)}".ljust(79) + "│")
        logger.info(f"│ Summary: {trend_report.summary[:60]}".ljust(79) + "│")
        
        if trend_report.trends:
            logger.info("│" + "─" * 78 + "│")
            for trend in trend_report.trends[:3]:  # Show first 3
                logger.info(f"│ • {trend.vital_name}".ljust(79) + "│")
                logger.info(f"│   Direction: {trend.direction.value}, Concern: {trend.concern_level}/3".ljust(79) + "│")
        logger.info("└" + "─" * 78 + "┘")
        logger.info("")
        
        # Conflict Agent Report
        logger.info("┌" + "─" * 78 + "┐")
        logger.info("│" + " ⚠️  CONFLICT AGENT REPORT".ljust(78) + "│")
        logger.info("├" + "─" * 78 + "┤")
        logger.info(f"│ Overall Severity: {conflict_report.overall_severity}/3".ljust(79) + "│")
        logger.info(f"│ Conflicts Detected: {len(conflict_report.conflicts)}".ljust(79) + "│")
        logger.info(f"│ Summary: {conflict_report.summary[:60]}".ljust(79) + "│")
        
        if conflict_report.conflicts:
            logger.info("│" + "─" * 78 + "│")
            for conflict in conflict_report.conflicts:
                conflict_name = conflict.conflict_type.value.replace('_', ' ').title()
                logger.info(f"│ • {conflict_name} (Severity: {conflict.severity}/3)".ljust(79) + "│")
                logger.info(f"│   {conflict.description[:70]}".ljust(79) + "│")
        logger.info("└" + "─" * 78 + "┘")
        logger.info("")
        
        # TimeBomb Agent Report
        logger.info("┌" + "─" * 78 + "┐")
        logger.info("│" + " ⏰ TIMEBOMB AGENT REPORT".ljust(78) + "│")
        logger.info("├" + "─" * 78 + "┤")
        logger.info(f"│ Overall Urgency: {timebomb_report.overall_urgency}/3".ljust(79) + "│")
        logger.info(f"│ Items Identified: {len(timebomb_report.timebombs)}".ljust(79) + "│")
        logger.info(f"│ Summary: {timebomb_report.summary[:60]}".ljust(79) + "│")
        
        if timebomb_report.timebombs:
            logger.info("│" + "─" * 78 + "│")
            for timebomb in timebomb_report.timebombs[:3]:  # Show first 3
                tb_name = timebomb.timebomb_type.value.replace('_', ' ').title()
                logger.info(f"│ • {tb_name} (Urgency: {timebomb.urgency}/3)".ljust(79) + "│")
                logger.info(f"│   {timebomb.description[:70]}".ljust(79) + "│")
        logger.info("└" + "─" * 78 + "┘")
        logger.info("")
    
    def _print_layer0_summary(self):
        """Print Layer 0 experiment summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("LAYER 0 EXPERIMENT SUMMARY")
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
        logger.info("   - Run Layer 1 experiment: python run_experiment.py --layer 1")
        logger.info("   - Implement Layer 2 coordinator")
        logger.info("=" * 80)
    
    def _print_layer1_summary(self):
        """Print Layer 1 experiment summary."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        logger.info("=" * 80)
        logger.info("LAYER 1 EXPERIMENT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"⏱️  Duration: {elapsed:.1f} seconds")
        logger.info(f"📦 PatientDataObjects processed: {self.pdo_count}")
        logger.info(f"✅ Experiment completed successfully")
        logger.info("")
        logger.info("📝 Notes:")
        logger.info("   - All three agents ran concurrently using asyncio.gather()")
        logger.info("   - Trend Agent: Analyzed vital sign trends")
        logger.info("   - Conflict Agent: Detected cross-signal patterns")
        logger.info("   - TimeBomb Agent: Identified forward-looking risks")
        logger.info("")
        logger.info("🎯 Next Steps:")
        logger.info("   - Implement Layer 2 coordinator to synthesize SBAR briefs")
        logger.info("   - Add LLM integration for enhanced reasoning")
        logger.info("=" * 80)


async def main(layer: int):
    """
    Main entry point for the experiment.
    
    Args:
        layer: Layer to test (0 or 1)
    """
    try:
        runner = ExperimentRunner(layer=layer, max_duration_seconds=60)
        runner.setup()
        
        if layer == 0:
            await runner.run_layer0_experiment()
        elif layer == 1:
            await runner.run_layer1_experiment()
        else:
            logger.error(f"❌ Invalid layer: {layer}. Must be 0 or 1.")
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 Experiment interrupted by user")
    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="ICU Silent Deterioration Spotter - Experimental Runner"
    )
    parser.add_argument(
        "--layer",
        type=int,
        choices=[0, 1],
        default=0,
        help="Layer to test: 0 (Emitter+Loader) or 1 (Emitter+Loader+Agents)"
    )
    args = parser.parse_args()
    
    # Print banner
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ICU SILENT DETERIORATION SPOTTER - EXPERIMENTAL RUNNER".center(78) + "║")
    print("║" + " " * 78 + "║")
    
    if args.layer == 0:
        print("║" + "  Layer 0: Emitter + Loader Test".center(78) + "║")
    elif args.layer == 1:
        print("║" + "  Layer 1: Emitter + Loader + Agents Test".center(78) + "║")
    
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    asyncio.run(main(args.layer))

# Made with Bob