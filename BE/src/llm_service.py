"""
Module: llm_service.py
Purpose: IBM watsonx.ai LLM integration for generating AI insights
Layer: Support

Part of ICU Silent Deterioration Spotter
Hackathon: IBM Bob Challenge 2026

This module provides LLM integration using IBM watsonx.ai for generating
clinical insights and reasoning for SBAR briefs.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import IBM watsonx.ai SDK
try:
    from ibm_watson_machine_learning.foundation_models import Model
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    logger.warning("IBM watsonx.ai SDK not available. Install with: pip install ibm-watson-machine-learning")


class LLMService:
    """
    Service for generating AI insights using IBM watsonx.ai LLM.
    """
    
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None, 
                 url: str = "https://us-south.ml.cloud.ibm.com"):
        """
        Initialize LLM service with IBM watsonx.ai credentials.
        
        Args:
            api_key: IBM Cloud API key
            project_id: watsonx.ai project ID
            url: watsonx.ai service URL
        """
        self.api_key = api_key
        self.project_id = project_id
        self.url = url
        self.model = None
        self.available = False
        
        if not WATSONX_AVAILABLE:
            logger.warning("IBM watsonx.ai SDK not installed. LLM features disabled.")
            return
        
        if not api_key or not project_id:
            logger.warning("IBM watsonx.ai credentials not provided. LLM features disabled.")
            return
        
        try:
            # Initialize the model
            self._initialize_model()
            self.available = True
            logger.info("IBM watsonx.ai LLM service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IBM watsonx.ai: {e}")
            self.available = False
    
    def _initialize_model(self):
        """Initialize the IBM watsonx.ai model."""
        if not WATSONX_AVAILABLE:
            return
        
        # Model parameters
        parameters = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 1,
            GenParams.REPETITION_PENALTY: 1.0
        }
        
        # Initialize model
        self.model = Model(
            model_id="ibm/granite-13b-chat-v2",  # Using IBM Granite model
            params=parameters,
            credentials={
                "apikey": self.api_key,
                "url": self.url
            },
            project_id=self.project_id
        )
    
    def generate_clinical_insight(self, patient_data: Dict[str, Any], 
                                  trend_summary: str, 
                                  conflict_summary: str,
                                  risk_level: str) -> str:
        """
        Generate clinical insight for a patient using LLM.
        
        Args:
            patient_data: Patient demographics and metadata
            trend_summary: Summary of vital trends
            conflict_summary: Summary of detected conflicts
            risk_level: Current risk level (GREEN, YELLOW, RED)
            
        Returns:
            AI-generated clinical insight text
        """
        if not self.available:
            return "AI insights unavailable - LLM service not configured."
        
        try:
            # Construct prompt
            prompt = self._build_clinical_prompt(
                patient_data, trend_summary, conflict_summary, risk_level
            )
            
            # Generate response
            response = self.model.generate_text(prompt=prompt)
            
            # Clean and return response
            insight = response.strip()
            logger.info(f"Generated AI insight for patient {patient_data.get('patient_id', 'unknown')}")
            return insight
            
        except Exception as e:
            logger.error(f"Error generating clinical insight: {e}")
            return f"Error generating AI insight: {str(e)}"
    
    def _build_clinical_prompt(self, patient_data: Dict[str, Any],
                               trend_summary: str,
                               conflict_summary: str,
                               risk_level: str) -> str:
        """
        Build a clinical prompt for the LLM.
        
        Args:
            patient_data: Patient information
            trend_summary: Vital trends summary
            conflict_summary: Conflict patterns summary
            risk_level: Risk level
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an expert ICU physician assistant analyzing patient data for signs of silent deterioration.

Patient Information:
- Age: {patient_data.get('age', 'unknown')} years
- Gender: {patient_data.get('gender', 'unknown')}
- Care Unit: {patient_data.get('careunit', 'unknown')}
- Current Risk Level: {risk_level}

Vital Trends Analysis:
{trend_summary}

Cross-Signal Patterns Detected:
{conflict_summary}

Based on this information, provide a concise clinical insight (2-3 sentences) that:
1. Identifies the most concerning pattern or trend
2. Explains the clinical significance
3. Suggests immediate monitoring priorities

Clinical Insight:"""
        
        return prompt
    
    def generate_trend_reasoning(self, vital_name: str, 
                                 current_value: float,
                                 slope: float,
                                 direction: str,
                                 concern_level: int) -> str:
        """
        Generate LLM reasoning for a vital trend.
        
        Args:
            vital_name: Name of the vital sign
            current_value: Current value
            slope: Rate of change
            direction: Trend direction
            concern_level: Concern level (0-3)
            
        Returns:
            AI-generated reasoning text
        """
        if not self.available:
            return f"{vital_name} is {direction} at {abs(slope):.1f} units/hour."
        
        try:
            prompt = f"""As an ICU physician, explain this vital sign trend in one clear sentence:

Vital: {vital_name}
Current Value: {current_value:.1f}
Trend: {direction} at {abs(slope):.1f} units/hour
Concern Level: {concern_level}/3

Provide a brief clinical interpretation:"""
            
            response = self.model.generate_text(prompt=prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating trend reasoning: {e}")
            return f"{vital_name} is {direction} at {abs(slope):.1f} units/hour."
    
    def generate_sbar_enhancement(self, situation: str, background: str,
                                  assessment: str, recommendation: str,
                                  risk_level: str) -> str:
        """
        Generate enhanced SBAR narrative using LLM.
        
        Args:
            situation: Current situation
            background: Background information
            assessment: Clinical assessment
            recommendation: Recommendations
            risk_level: Risk level
            
        Returns:
            Enhanced SBAR narrative
        """
        if not self.available:
            return "AI enhancement unavailable."
        
        try:
            prompt = f"""As an ICU physician, review this SBAR brief and provide a concise summary highlighting the key clinical concerns:

SITUATION: {situation}

BACKGROUND: {background}

ASSESSMENT: {assessment}

RECOMMENDATION: {recommendation}

Risk Level: {risk_level}

Provide a 2-3 sentence clinical summary focusing on the most critical findings:"""
            
            response = self.model.generate_text(prompt=prompt)
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating SBAR enhancement: {e}")
            return "Error generating enhanced summary."


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service(api_key: Optional[str] = None, 
                   project_id: Optional[str] = None,
                   url: str = "https://us-south.ml.cloud.ibm.com") -> LLMService:
    """
    Get or create the global LLM service instance.
    
    Args:
        api_key: IBM Cloud API key
        project_id: watsonx.ai project ID
        url: watsonx.ai service URL
        
    Returns:
        LLMService instance
    """
    global _llm_service
    
    if _llm_service is None:
        _llm_service = LLMService(api_key=api_key, project_id=project_id, url=url)
    
    return _llm_service


def initialize_llm_from_config():
    """
    Initialize LLM service from config settings.
    
    Returns:
        LLMService instance
    """
    from config.config import config
    
    return get_llm_service(
        api_key=config.WATSONX_API_KEY,
        project_id=config.WATSONX_PROJECT_ID,
        url=config.WATSONX_URL
    )


# Made with Bob