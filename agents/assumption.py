"""
Assumption Agent - Makes implicit assumptions explicit
"""
from typing import List
from agents.base_agent import BaseAgent
from core.schemas import (
    AssumptionAgentOutput, Assumption,
    QueryProcessorOutput, FactBoundaryOutput
)
from core.prompts import PROMPTS

class AssumptionAgent(BaseAgent):
    """
    Agent 3: Assumption Agent
    Makes implicit assumptions explicit and assesses their risk
    """
    
    def process(self, user_query: str, 
                query_processor_output: QueryProcessorOutput,
                fact_boundary_output: FactBoundaryOutput) -> AssumptionAgentOutput:
        """Identify and assess assumptions using LLM"""
        self.logger.info("Identifying assumptions...")
        
        # Prepare prompt
        system_prompt = PROMPTS["assumption"]["system"]
        user_prompt = self._format_prompt(
            PROMPTS["assumption"]["user_template"],
            user_query=user_query,
            query_processor_json=query_processor_output.to_json(),
            fact_boundary_json=fact_boundary_output.to_json()
        )
        
        # Get LLM response
        response = self.llm.complete_json(system_prompt, user_prompt)
        
        # Parse and validate
        assumptions = [
            Assumption(**assumption) for assumption in response.get("assumptions", [])
        ]
        
        return AssumptionAgentOutput(
            assumptions=assumptions,
            overall_assumption_risk=response.get("overall_assumption_risk", "medium"),
            notes=response.get("notes", "")
        )
