"""
Unknown Detection Agent - Identifies missing critical information
"""
from typing import List
from agents.base_agent import BaseAgent
from core.schemas import (
    UnknownDetectionOutput, MissingInformation,
    QueryProcessorOutput, FactBoundaryOutput, AssumptionAgentOutput
)
from core.prompts import PROMPTS
from config.settings import settings

class UnknownDetectionAgent(BaseAgent):
    """
    Agent 4: Unknown Detection Agent
    Identifies missing but critical information required for safe recommendations
    """
    
    def process(self, user_query: str,
                query_processor_output: QueryProcessorOutput,
                fact_boundary_output: FactBoundaryOutput,
                assumption_agent_output: AssumptionAgentOutput) -> UnknownDetectionOutput:
        """Identify missing critical information using LLM (optionally with inner council)"""
        self.logger.info("Detecting unknowns...")
        
        # Prepare prompt
        system_prompt = PROMPTS["unknown_detection"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["unknown_detection"]["user_template"],
            user_query=user_query,
            query_processor_json=query_processor_output.to_json(),
            fact_boundary_json=fact_boundary_output.to_json(),
            assumption_json=assumption_agent_output.to_json()
        )
        
        if settings.ENABLE_INNER_COUNCIL:
            # Use inner council for this critical agent
            return self._process_with_inner_council(system_prompt, user_prompt)
        else:
            # Single LLM call
            response = self.llm.complete_json(system_prompt, user_prompt)
            return self._parse_response(response)
    
    def _process_with_inner_council(self, system_prompt: str, user_prompt: str) -> UnknownDetectionOutput:
        """Process using inner LLM council"""
        self.logger.info(f"Using inner council with {settings.INNER_COUNCIL_SIZE} models...")
        
        responses = self.llm.complete_json_multiple(
            system_prompt, user_prompt, 
            n=settings.INNER_COUNCIL_SIZE
        )
        
        # Aggregate responses
        return self._aggregate_unknown_detection(responses)
    
    def _aggregate_unknown_detection(self, responses: List[dict]) -> UnknownDetectionOutput:
        """Aggregate multiple Unknown Detection responses"""
        # Collect all missing information across responses
        all_missing = {}
        
        for response in responses:
            for item in response.get("missing_information", []):
                field_name = item["field_name"]
                if field_name not in all_missing:
                    all_missing[field_name] = {
                        "count": 0,
                        "data": item
                    }
                all_missing[field_name]["count"] += 1
        
        # Keep fields mentioned by at least majority
        threshold = len(responses) // 2 + 1
        final_missing = [
            MissingInformation(**data["data"])
            for field, data in all_missing.items()
            if data["count"] >= threshold
        ]
        
        # Average completeness score
        avg_completeness = sum(
            r.get("information_completeness_score", 0.0) for r in responses
        ) / len(responses)
        
        # Combine notes
        notes = f"Inner council consensus: {len(final_missing)} critical unknowns (from {len(responses)} model runs). "
        notes += responses[0].get("notes", "")
        
        return UnknownDetectionOutput(
            missing_information=final_missing,
            information_completeness_score=round(avg_completeness, 2),
            notes=notes
        )
    
    def _parse_response(self, response: dict) -> UnknownDetectionOutput:
        """Parse single LLM response"""
        missing_info = [
            MissingInformation(**item) 
            for item in response.get("missing_information", [])
        ]
        
        return UnknownDetectionOutput(
            missing_information=missing_info,
            information_completeness_score=float(response.get("information_completeness_score", 0.0)),
            notes=response.get("notes", "")
        )
