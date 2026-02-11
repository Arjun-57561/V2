from agents.base_agent import BaseAgent
from core.schemas import AgentResponse, UncertaintyType
from core.prompts import ASSUMPTION_PROMPT

class AssumptionDetection(BaseAgent):
    def __init__(self):
        super().__init__("AssumptionDetection")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = ASSUMPTION_PROMPT.format(content=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.8,
            uncertainty_flags=[UncertaintyType.ASSUMPTION]
        )
