"""
Fact Boundary Agent - Identifies definite facts
"""
from typing import List
from agents.base_agent import BaseAgent
from core.schemas import (
    FactBoundaryOutput, KnownFact, QueryProcessorOutput
)
from core.prompts import PROMPTS

class FactBoundaryAgent(BaseAgent):
    """
    Agent 2: Fact Boundary Agent
    Identifies what is CERTAINLY TRUE given user query and parsed entities
    """
    
    def process(self, user_query: str, query_processor_output: QueryProcessorOutput) -> FactBoundaryOutput:
        """Identify definite facts using LLM"""
        self.logger.info("Extracting facts...")
        
        # Prepare prompt
        system_prompt = PROMPTS["fact_boundary"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["fact_boundary"]["user_template"],
            user_query=user_query,
            query_processor_json=query_processor_output.to_json()
        )
        
        # Get LLM response
        response = self.llm.complete_json(system_prompt, user_prompt)
        
        # Parse and validate
        known_facts = [
            KnownFact(**fact) for fact in response.get("known_facts", [])
        ]
        
        return FactBoundaryOutput(
            known_facts=known_facts,
            clarity_score=float(response.get("clarity_score", 0.0)),
            explanatory_notes=response.get("explanatory_notes", "")
        )
