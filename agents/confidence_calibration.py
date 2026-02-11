from agents.base_agent import BaseAgent
from core.schemas import AgentResponse
from core.prompts import CONFIDENCE_CALIBRATION_PROMPT

class ConfidenceCalibration(BaseAgent):
    def __init__(self):
        super().__init__("ConfidenceCalibration")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = CONFIDENCE_CALIBRATION_PROMPT.format(content=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.9
        )
