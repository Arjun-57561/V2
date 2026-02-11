"""
Confidence Calibration Agent - Calibrates confidence and sets safety flag
"""
from agents.base_agent import BaseAgent
from core.schemas import (
    ConfidenceCalibrationOutput, EpistemicUncertaintyFactor,
    QueryProcessorOutput, FactBoundaryOutput, AssumptionAgentOutput,
    UnknownDetectionOutput, TemporalUncertaintyOutput
)
from core.prompts import PROMPTS

class ConfidenceCalibrationAgent(BaseAgent):
    """
    Agent 6: Confidence Calibration Agent
    Converts council's analysis into calibrated confidence score and safety flag
    """
    
    def process(self, query_processor_output: QueryProcessorOutput,
                fact_boundary_output: FactBoundaryOutput,
                assumption_agent_output: AssumptionAgentOutput,
                unknown_detection_output: UnknownDetectionOutput,
                temporal_agent_output: TemporalUncertaintyOutput) -> ConfidenceCalibrationOutput:
        """Calibrate confidence based on all agent outputs using LLM"""
        self.logger.info("Calibrating confidence...")
        
        # Prepare prompt
        system_prompt = PROMPTS["confidence"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["confidence"]["user_template"],
            query_processor_json=query_processor_output.to_json(),
            fact_boundary_json=fact_boundary_output.to_json(),
            assumption_json=assumption_agent_output.to_json(),
            unknown_detection_json=unknown_detection_output.to_json(),
            temporal_json=temporal_agent_output.to_json()
        )
        
        # Get LLM response
        response = self.llm.complete_json(system_prompt, user_prompt)
        
        # Parse and validate
        uncertainty_factors = [
            EpistemicUncertaintyFactor(**factor)
            for factor in response.get("epistemic_uncertainty_factors", [])
        ]
        
        return ConfidenceCalibrationOutput(
            calibrated_confidence=int(response.get("calibrated_confidence", 0)),
            epistemic_uncertainty_factors=uncertainty_factors,
            confidence_explanation=response.get("confidence_explanation", ""),
            safety_flag=response.get("safety_flag", "answer_with_caution")
        )
