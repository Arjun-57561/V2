from typing import List
from agents.query_processor import QueryProcessor
from agents.fact_boundary import FactBoundary
from agents.assumption import AssumptionDetection
from agents.unknown_detection import UnknownDetection
from agents.temporal_uncertainty import TemporalUncertainty
from agents.confidence_calibration import ConfidenceCalibration
from agents.decision_guidance import DecisionGuidance
from core.schemas import CouncilDecision, AgentResponse
from council.aggregator import Aggregator

class CouncilOrchestrator:
    def __init__(self):
        self.agents = [
            QueryProcessor(),
            FactBoundary(),
            AssumptionDetection(),
            UnknownDetection(),
            TemporalUncertainty(),
            ConfidenceCalibration(),
            DecisionGuidance()
        ]
        self.aggregator = Aggregator()
    
    def process_query(self, query: str) -> CouncilDecision:
        responses: List[AgentResponse] = []
        
        for agent in self.agents:
            response = agent.process(query)
            responses.append(response)
        
        return self.aggregator.aggregate(responses)
