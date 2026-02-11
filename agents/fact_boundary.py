from agents.base_agent import BaseAgent
from core.schemas import AgentResponse, UncertaintyType
from core.prompts import FACT_BOUNDARY_PROMPT

class FactBoundary(BaseAgent):
    def __init__(self):
        super().__init__("FactBoundary")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = FACT_BOUNDARY_PROMPT.format(content=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.85,
            uncertainty_flags=[UncertaintyType.FACTUAL]
        )
