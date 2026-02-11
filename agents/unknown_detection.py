from agents.base_agent import BaseAgent
from core.schemas import AgentResponse, UncertaintyType
from core.prompts import UNKNOWN_DETECTION_PROMPT

class UnknownDetection(BaseAgent):
    def __init__(self):
        super().__init__("UnknownDetection")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = UNKNOWN_DETECTION_PROMPT.format(content=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.75,
            uncertainty_flags=[UncertaintyType.UNKNOWN]
        )
