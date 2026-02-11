"""
Data schemas for Uncertainty-First Agent Council
"""
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import List, Optional, Dict, Any
import json

# ==================== ENUMS ====================

class Domain(str, Enum):
    GOVERNMENT_SCHEME = "government_scheme"
    LEGAL_PRESCREENING = "legal_prescreening"
    FINANCIAL_COMPLIANCE = "financial_compliance"
    OTHER = "other"

class Category(str, Enum):
    SC = "SC"
    ST = "ST"
    OBC = "OBC"
    GENERAL = "General"
    EWS = "EWS"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ImportanceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class SafetyFlag(str, Enum):
    SAFE_TO_ANSWER = "safe_to_answer"
    ANSWER_WITH_CAUTION = "answer_with_caution"
    UNSAFE_TO_ANSWER = "unsafe_to_answer"

class AnswerStyle(str, Enum):
    NO_DIRECT_DECISION = "no_direct_decision"
    CAUTIOUS_TENTATIVE_DECISION = "cautious_tentative_decision"
    DIRECT_DECISION = "direct_decision"

# ==================== BASE CLASSES ====================

@dataclass
class BaseOutput:
    """Base class for all agent outputs"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

# ==================== QUERY PROCESSOR ====================

@dataclass
class QueryEntities:
    age: Optional[int] = None
    monthly_income: Optional[float] = None
    annual_income: Optional[float] = None
    state_or_ut: Optional[str] = None
    category: Optional[str] = None
    occupation: Optional[str] = None
    documents_mentioned: List[str] = field(default_factory=list)

@dataclass
class QueryProcessorOutput(BaseOutput):
    cleaned_query: str
    detected_domain: str
    entities: QueryEntities
    ambiguity_flags: List[str]
    notes: str

# ==================== FACT BOUNDARY ====================

@dataclass
class KnownFact:
    fact_id: str
    description: str
    source: str

@dataclass
class FactBoundaryOutput(BaseOutput):
    known_facts: List[KnownFact]
    clarity_score: float
    explanatory_notes: str

# ==================== ASSUMPTION ====================

@dataclass
class Assumption:
    assumption_id: str
    description: str
    risk_level: str
    impact_if_wrong: str

@dataclass
class AssumptionAgentOutput(BaseOutput):
    assumptions: List[Assumption]
    overall_assumption_risk: str
    notes: str

# ==================== UNKNOWN DETECTION ====================

@dataclass
class MissingInformation:
    unknown_id: str
    field_name: str
    description: str
    importance_level: str
    consequence_if_ignored: str

@dataclass
class UnknownDetectionOutput(BaseOutput):
    missing_information: List[MissingInformation]
    information_completeness_score: float
    notes: str

# ==================== TEMPORAL UNCERTAINTY ====================

@dataclass
class TimeDependentFactor:
    factor_id: str
    description: str
    risk_if_outdated: str

@dataclass
class TemporalUncertaintyOutput(BaseOutput):
    time_sensitivity_level: str
    time_dependent_factors: List[TimeDependentFactor]
    recommended_fresh_checks: List[str]
    notes: str

# ==================== CONFIDENCE CALIBRATION ====================

@dataclass
class EpistemicUncertaintyFactor:
    factor_id: str
    description: str
    severity: str

@dataclass
class ConfidenceCalibrationOutput(BaseOutput):
    calibrated_confidence: int
    epistemic_uncertainty_factors: List[EpistemicUncertaintyFactor]
    confidence_explanation: str
    safety_flag: str

# ==================== DECISION GUIDANCE ====================

@dataclass
class DecisionGuidanceOutput(BaseOutput):
    final_answer_style: str
    user_friendly_summary: str
    explicit_knowns: List[str]
    explicit_unknowns: List[str]
    assumptions_highlighted: List[str]
    calibrated_confidence: int
    safety_flag: str
    recommended_next_steps: List[str]

# ==================== COUNCIL OUTPUT ====================

@dataclass
class CouncilOutput(BaseOutput):
    """Final aggregated output from the council"""
    query: str
    domain: str
    
    # Agent outputs
    query_processor: QueryProcessorOutput
    fact_boundary: FactBoundaryOutput
    assumption: AssumptionAgentOutput
    unknown_detection: UnknownDetectionOutput
    temporal: TemporalUncertaintyOutput
    confidence: ConfidenceCalibrationOutput
    decision: DecisionGuidanceOutput
    
    # Meta information
    processing_time_seconds: float = 0.0
    inner_council_enabled: bool = False
