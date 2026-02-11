"""
Response Aggregator - Formats council output for users
"""
from core.schemas import CouncilOutput
from utils.logger import get_logger

class ResponseAggregator:
    """Aggregates and formats council outputs for end users"""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def format_user_response(self, council_output: CouncilOutput) -> str:
        """
        Format council output as user-friendly text
        
        Args:
            council_output: Full council analysis
            
        Returns:
            Formatted multi-line string
        """
        decision = council_output.decision
        confidence = council_output.confidence
        
        lines = []
        
        # Header
        lines.append("\n" + "="*80)
        lines.append("UNCERTAINTY-AWARE RESPONSE".center(80))
        lines.append("="*80 + "\n")
        
        # Safety warning
        safety_icons = {
            "safe_to_answer": "✅",
            "answer_with_caution": "⚠️",
            "unsafe_to_answer": "🛑"
        }
        
        safety_messages = {
            "safe_to_answer": "SAFE TO PROCEED",
            "answer_with_caution": "PROCEED WITH CAUTION",
            "unsafe_to_answer": "DO NOT PROCEED WITHOUT MORE INFORMATION"
        }
        
        icon = safety_icons.get(decision.safety_flag, "⚠️")
        message = safety_messages.get(decision.safety_flag, "CAUTION ADVISED")
        
        lines.append(f"{icon} Safety Assessment: {message}")
        lines.append(f"📊 Confidence Level: {decision.calibrated_confidence}%")
        lines.append(f"🎯 Recommendation Type: {decision.final_answer_style.replace('_', ' ').title()}\n")
        
        # Summary
        lines.append("📝 SUMMARY")
        lines.append("-" * 80)
        lines.append(decision.user_friendly_summary)
        lines.append("")
        
        # What we know
        if decision.explicit_knowns:
            lines.append("✅ WHAT WE KNOW")
            lines.append("-" * 80)
            for i, known in enumerate(decision.explicit_knowns, 1):
                lines.append(f"  {i}. {known}")
            lines.append("")
        
        # What we don't know
        if decision.explicit_unknowns:
            lines.append("❓ WHAT WE DON'T KNOW (Critical Gaps)")
            lines.append("-" * 80)
            for i, unknown in enumerate(decision.explicit_unknowns, 1):
                lines.append(f"  {i}. {unknown}")
            lines.append("")
        
        # Assumptions being made
        if decision.assumptions_highlighted:
            lines.append("🤔 ASSUMPTIONS WE'RE MAKING")
            lines.append("-" * 80)
            for i, assumption in enumerate(decision.assumptions_highlighted, 1):
                lines.append(f"  {i}. {assumption}")
            lines.append("")
        
        # Recommended next steps
        if decision.recommended_next_steps:
            lines.append("🎯 RECOMMENDED NEXT STEPS")
            lines.append("-" * 80)
            for i, step in enumerate(decision.recommended_next_steps, 1):
                lines.append(f"  {i}. {step}")
            lines.append("")
        
        # Uncertainty factors
        if confidence.epistemic_uncertainty_factors:
            lines.append("⚠️  UNCERTAINTY FACTORS")
            lines.append("-" * 80)
            for factor in confidence.epistemic_uncertainty_factors:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(factor.severity, "🟡")
                lines.append(f"  {severity_icon} {factor.description}")
            lines.append("")
        
        # Footer
        lines.append("-" * 80)
        lines.append(f"ℹ️  Domain: {council_output.domain.replace('_', ' ').title()}")
        lines.append(f"⏱️  Processing time: {council_output.processing_time_seconds}s")
        if council_output.inner_council_enabled:
            lines.append("🔬 Inner council mode: ENABLED (multiple model consensus)")
        lines.append("="*80 + "\n")
        
        return "\n".join(lines)
    
    def format_compact_response(self, council_output: CouncilOutput) -> str:
        """
        Format a compact version for APIs or logging
        
        Args:
            council_output: Full council analysis
            
        Returns:
            Compact formatted string
        """
        decision = council_output.decision
        
        return f"""
Query: {council_output.query}
Confidence: {decision.calibrated_confidence}%
Safety: {decision.safety_flag}
Summary: {decision.user_friendly_summary}
Unknowns: {len(decision.explicit_unknowns)}
Next Steps: {len(decision.recommended_next_steps)}
"""
