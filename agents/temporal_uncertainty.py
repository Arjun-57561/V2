from agents.base_agent import BaseAgent
from core.schemas import AgentResponse, UncertaintyType
from core.prompts import TEMPORAL_UNCERTAINTY_PROMPT

class TemporalUncertainty(BaseAgent):
    def __init__(self):
        super().__init__("TemporalUncertainty")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = TEMPORAL_UNCERTAINTY_PROMPT.format(content=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.8,
            uncertainty_flags=[UncertaintyType.TEMPORAL]
        )
