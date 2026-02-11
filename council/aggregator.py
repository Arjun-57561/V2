from typing import List
from core.schemas import AgentResponse, CouncilDecision

class Aggregator:
    def aggregate(self, responses: List[AgentResponse]) -> CouncilDecision:
        avg_confidence = sum(r.confidence for r in responses) / len(responses)
        
        combined_content = "\n\n".join([
            f"[{r.agent_name}]: {r.content}" for r in responses
        ])
        
        warnings = []
        if avg_confidence < 0.7:
            warnings.append("Low overall confidence in response")
        
        return CouncilDecision(
            final_response=combined_content,
            confidence_score=avg_confidence,
            agent_responses=responses,
            warnings=warnings
        )
