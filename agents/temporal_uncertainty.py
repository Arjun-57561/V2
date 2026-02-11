"""
Temporal Uncertainty Agent - Identifies time-dependent factors
"""
from agents.base_agent import BaseAgent
from core.schemas import (
    TemporalUncertaintyOutput, TimeDependentFactor,
    QueryProcessorOutput, FactBoundaryOutput, UnknownDetectionOutput
)
from core.prompts import PROMPTS

class TemporalUncertaintyAgent(BaseAgent):
    """
    Agent 5: Temporal Uncertainty Agent
    Identifies how time-dependent the answer is (rule changes, deadlines, etc.)
    """
    
    def process(self, user_query: str,
                query_processor_output: QueryProcessorOutput,
                fact_boundary_output: FactBoundaryOutput,
                unknown_detection_output: UnknownDetectionOutput) -> TemporalUncertaintyOutput:
        """Identify time-related uncertainties using LLM"""
        self.logger.info("Analyzing temporal uncertainty...")
        
        # Prepare prompt
        system_prompt = PROMPTS["temporal"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["temporal"]["user_template"],
            user_query=user_query,
            query_processor_json=query_processor_output.to_json(),
            fact_boundary_json=fact_boundary_output.to_json(),
            unknown_detection_json=unknown_detection_output.to_json()
        )
        
        # Get LLM response
        response = self.llm.complete_json(system_prompt, user_prompt)
        
        # Parse and validate
        time_factors = [
            TimeDependentFactor(**factor)
            for factor in response.get("time_dependent_factors", [])
        ]
        
        return TemporalUncertaintyOutput(
            time_sensitivity_level=response.get("time_sensitivity_level", "medium"),
            time_dependent_factors=time_factors,
            recommended_fresh_checks=response.get("recommended_fresh_checks", []),
            notes=response.get("notes", "")
        )
