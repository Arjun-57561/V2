from agents.base_agent import BaseAgent
from core.schemas import AgentResponse
from core.prompts import DECISION_GUIDANCE_PROMPT

class DecisionGuidance(BaseAgent):
    def __init__(self):
        super().__init__("DecisionGuidance")
    
    def process(self, input_data: str) -> AgentResponse:
        prompt = DECISION_GUIDANCE_PROMPT.format(analyses=input_data)
        response = self.llm.generate(prompt)
        return AgentResponse(
            agent_name=self.name,
            content=response,
            confidence=0.85
        )
