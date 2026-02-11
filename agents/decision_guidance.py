"""
Decision Guidance Agent - Produces final user-facing guidance
"""
from typing import List
from agents.base_agent import BaseAgent
from core.schemas import (
    DecisionGuidanceOutput,
    QueryProcessorOutput, FactBoundaryOutput, AssumptionAgentOutput,
    UnknownDetectionOutput, TemporalUncertaintyOutput, ConfidenceCalibrationOutput
)
from core.prompts import PROMPTS
from config.settings import settings

class DecisionGuidanceAgent(BaseAgent):
    """
    Agent 7: Decision Guidance Agent
    Converts council's analysis into clear guidance for the user
    """
    
    def process(self, user_query: str,
                query_processor_output: QueryProcessorOutput,
                fact_boundary_output: FactBoundaryOutput,
                assumption_agent_output: AssumptionAgentOutput,
                unknown_detection_output: UnknownDetectionOutput,
                temporal_agent_output: TemporalUncertaintyOutput,
                confidence_agent_output: ConfidenceCalibrationOutput) -> DecisionGuidanceOutput:
        """Produce structured guidance using LLM (optionally with inner council)"""
        self.logger.info("Generating decision guidance...")
        
        # Prepare prompt
        system_prompt = PROMPTS["decision_guidance"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["decision_guidance"]["user_template"],
            user_query=user_query,
            query_processor_json=query_processor_output.to_json(),
            fact_boundary_json=fact_boundary_output.to_json(),
            assumption_json=assumption_agent_output.to_json(),
            unknown_detection_json=unknown_detection_output.to_json(),
            temporal_json=temporal_agent_output.to_json(),
            confidence_json=confidence_agent_output.to_json()
        )
        
        if settings.ENABLE_INNER_COUNCIL:
            # Use inner council for this critical agent
            return self._process_with_inner_council(system_prompt, user_prompt)
        else:
            # Single LLM call
            response = self.llm.complete_json(system_prompt, user_prompt)
            return self._parse_response(response)
    
    def _process_with_inner_council(self, system_prompt: str, user_prompt: str) -> DecisionGuidanceOutput:
        """Process using inner LLM council"""
        self.logger.info(f"Using inner council with {settings.INNER_COUNCIL_SIZE} models...")
        
        responses = self.llm.complete_json_multiple(
            system_prompt, user_prompt,
            n=settings.INNER_COUNCIL_SIZE
        )
        
        # Aggregate responses (most conservative approach)
        return self._aggregate_decision_guidance(responses)
    
    def _aggregate_decision_guidance(self, responses: List[dict]) -> DecisionGuidanceOutput:
        """Aggregate multiple Decision Guidance responses (conservative)"""
        
        # Most conservative safety flag
        safety_priority = {
            "unsafe_to_answer": 3,
            "answer_with_caution": 2,
            "safe_to_answer": 1
        }
        
        most_conservative_flag = max(
            [r.get("safety_flag", "answer_with_caution") for r in responses],
            key=lambda x: safety_priority.get(x, 2)
        )
        
        # Minimum confidence
        min_confidence = min(
            r.get("calibrated_confidence", 0) for r in responses
        )
        
        # Union of all knowns, unknowns, assumptions
        all_knowns = set()
        all_unknowns = set()
        all_assumptions = set()
        all_next_steps = set()
        
        for r in responses:
            all_knowns.update(r.get("explicit_knowns", []))
            all_unknowns.update(r.get("explicit_unknowns", []))
            all_assumptions.update(r.get("assumptions_highlighted", []))
            all_next_steps.update(r.get("recommended_next_steps", []))
        
        # Use first response's summary as base
        summary = f"[Consensus from {len(responses)} models] " + responses[0].get("user_friendly_summary", "")
        
        # Map safety flag to answer style
        answer_style_map = {
            "unsafe_to_answer": "no_direct_decision",
            "answer_with_caution": "cautious_tentative_decision",
            "safe_to_answer": "direct_decision"
        }
        
        return DecisionGuidanceOutput(
            final_answer_style=answer_style_map.get(most_conservative_flag, "cautious_tentative_decision"),
            user_friendly_summary=summary,
            explicit_knowns=sorted(list(all_knowns)),
            explicit_unknowns=sorted(list(all_unknowns)),
            assumptions_highlighted=sorted(list(all_assumptions)),
            calibrated_confidence=min_confidence,
            safety_flag=most_conservative_flag,
            recommended_next_steps=sorted(list(all_next_steps))
        )
    
    def _parse_response(self, response: dict) -> DecisionGuidanceOutput:
        """Parse single LLM response"""
        return DecisionGuidanceOutput(
            final_answer_style=response.get("final_answer_style", "cautious_tentative_decision"),
            user_friendly_summary=response.get("user_friendly_summary", ""),
            explicit_knowns=response.get("explicit_knowns", []),
            explicit_unknowns=response.get("explicit_unknowns", []),
            assumptions_highlighted=response.get("assumptions_highlighted", []),
            calibrated_confidence=int(response.get("calibrated_confidence", 0)),
            safety_flag=response.get("safety_flag", "answer_with_caution"),
            recommended_next_steps=response.get("recommended_next_steps", [])
        )
