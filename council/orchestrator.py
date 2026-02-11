"""
Main Council Orchestrator - Coordinates all agents
"""
import time
from typing import Optional
from core.llm_client import LLMClient
from core.schemas import CouncilOutput
from agents import (
    QueryProcessorAgent,
    FactBoundaryAgent,
    AssumptionAgent,
    UnknownDetectionAgent,
    TemporalUncertaintyAgent,
    ConfidenceCalibrationAgent,
    DecisionGuidanceAgent
)
from council.aggregator import ResponseAggregator
from utils.logger import get_logger
from config.settings import settings

class UncertaintyFirstCouncil:
    """
    Main orchestrator for the Uncertainty-First Agent Council
    Coordinates all agents and manages the processing pipeline
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        Initialize the council with all agents
        
        Args:
            llm_client: Optional LLM client (creates new one if not provided)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.llm = llm_client or LLMClient()
        
        # Initialize all agents
        self.query_processor = QueryProcessorAgent(self.llm)
        self.fact_boundary = FactBoundaryAgent(self.llm)
        self.assumption = AssumptionAgent(self.llm)
        self.unknown_detection = UnknownDetectionAgent(self.llm)
        self.temporal = TemporalUncertaintyAgent(self.llm)
        self.confidence = ConfidenceCalibrationAgent(self.llm)
        self.decision_guidance = DecisionGuidanceAgent(self.llm)
        
        self.aggregator = ResponseAggregator()
        
        self.logger.info("Uncertainty-First Council initialized successfully")
        self.logger.info(f"Inner council mode: {'ENABLED' if settings.ENABLE_INNER_COUNCIL else 'DISABLED'}")
    
    def process_query(self, user_query: str, verbose: bool = True) -> CouncilOutput:
        """
        Process a user query through the entire council pipeline
        
        Args:
            user_query: Natural language user query
            verbose: Whether to print progress
            
        Returns:
            CouncilOutput with all agent results and final decision
        """
        start_time = time.time()
        
        if verbose:
            self._print_header("UNCERTAINTY-FIRST AGENT COUNCIL")
            print(f"\n📝 Query: {user_query}\n")
        
        try:
            # Stage 1: Query Processing
            if verbose:
                print("🔄 Stage 1: Query Processing...")
            qp_output = self.query_processor.process(user_query)
            if verbose:
                print(f"   ✓ Domain: {qp_output.detected_domain}")
                print(f"   ✓ Entities extracted: {self._count_entities(qp_output)}/6")
                print(f"   ✓ Ambiguities: {len(qp_output.ambiguity_flags)}")
            
            # Stage 2: Fact Boundary Analysis
            if verbose:
                print("\n🔍 Stage 2: Fact Boundary Analysis...")
            fb_output = self.fact_boundary.process(user_query, qp_output)
            if verbose:
                print(f"   ✓ Known facts identified: {len(fb_output.known_facts)}")
                print(f"   ✓ Clarity score: {fb_output.clarity_score:.2f}")
            
            # Stage 3: Assumption Detection
            if verbose:
                print("\n🤔 Stage 3: Assumption Detection...")
            assumption_output = self.assumption.process(user_query, qp_output, fb_output)
            if verbose:
                print(f"   ✓ Assumptions identified: {len(assumption_output.assumptions)}")
                print(f"   ✓ Overall risk: {assumption_output.overall_assumption_risk.upper()}")
            
            # Stage 4: Unknown Detection
            if verbose:
                print("\n❓ Stage 4: Unknown Detection...")
            unknown_output = self.unknown_detection.process(
                user_query, qp_output, fb_output, assumption_output
            )
            if verbose:
                if settings.ENABLE_INNER_COUNCIL:
                    print(f"   ℹ️  Using inner council ({settings.INNER_COUNCIL_SIZE} models)")
                print(f"   ✓ Missing information: {len(unknown_output.missing_information)}")
                print(f"   ✓ Completeness: {unknown_output.information_completeness_score:.2f}")
            
            # Stage 5: Temporal Uncertainty
            if verbose:
                print("\n⏰ Stage 5: Temporal Uncertainty Analysis...")
            temporal_output = self.temporal.process(
                user_query, qp_output, fb_output, unknown_output
            )
            if verbose:
                print(f"   ✓ Time sensitivity: {temporal_output.time_sensitivity_level.upper()}")
                print(f"   ✓ Time-dependent factors: {len(temporal_output.time_dependent_factors)}")
            
            # Stage 6: Confidence Calibration
            if verbose:
                print("\n📊 Stage 6: Confidence Calibration...")
            confidence_output = self.confidence.process(
                qp_output, fb_output, assumption_output, unknown_output, temporal_output
            )
            if verbose:
                print(f"   ✓ Calibrated confidence: {confidence_output.calibrated_confidence}%")
                print(f"   ✓ Safety flag: {confidence_output.safety_flag.upper()}")
            
            # Stage 7: Decision Guidance
            if verbose:
                print("\n🎯 Stage 7: Decision Guidance Generation...")
            decision_output = self.decision_guidance.process(
                user_query, qp_output, fb_output, assumption_output,
                unknown_output, temporal_output, confidence_output
            )
            if verbose:
                if settings.ENABLE_INNER_COUNCIL:
                    print(f"   ℹ️  Using inner council ({settings.INNER_COUNCIL_SIZE} models)")
                print(f"   ✓ Answer style: {decision_output.final_answer_style}")
                print(f"   ✓ Next steps: {len(decision_output.recommended_next_steps)}")
            
            # Create final output
            processing_time = time.time() - start_time
            
            council_output = CouncilOutput(
                query=user_query,
                domain=qp_output.detected_domain,
                query_processor=qp_output,
                fact_boundary=fb_output,
                assumption=assumption_output,
                unknown_detection=unknown_output,
                temporal=temporal_output,
                confidence=confidence_output,
                decision=decision_output,
                processing_time_seconds=round(processing_time, 2),
                inner_council_enabled=settings.ENABLE_INNER_COUNCIL
            )
            
            if verbose:
                print(f"\n⏱️  Total processing time: {processing_time:.2f}s")
                print("\n" + "="*80)
            
            return council_output
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}", exc_info=True)
            raise
    
    def get_user_friendly_response(self, council_output: CouncilOutput) -> str:
        """
        Convert council output to user-friendly text response
        
        Args:
            council_output: Full council output
            
        Returns:
            Formatted string response for end users
        """
        return self.aggregator.format_user_response(council_output)
    
    def _count_entities(self, qp_output) -> int:
        """Count extracted entities"""
        entities = qp_output.entities
        return sum([
            entities.age is not None,
            entities.annual_income is not None,
            entities.state_or_ut is not None,
            entities.category is not None,
            entities.occupation is not None,
            len(entities.documents_mentioned) > 0
        ])
    
    def _print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "="*80)
        print(text.center(80))
        print("="*80)
