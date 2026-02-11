"""
Test scenarios for the Uncertainty-First Agent Council
"""
import unittest
from council.orchestrator import UncertaintyFirstCouncil
from core.schemas import SafetyFlag

class TestScenarios(unittest.TestCase):
    """Test various real-world scenarios"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize council once for all tests"""
        cls.council = UncertaintyFirstCouncil()
    
    def test_complete_information_query(self):
        """Test query with complete information"""
        query = "I am 25 years old, earning 3 LPA annually, from Maharashtra, OBC category, I have Aadhaar and income certificate. Am I eligible for any schemes?"
        
        output = self.council.process_query(query, verbose=False)
        
        # Should have high confidence
        self.assertGreater(output.confidence.calibrated_confidence, 40)
        
        # Should have identified several facts
        self.assertGreater(len(output.fact_boundary.known_facts), 3)
        
        print(f"\n✓ Complete info test: Confidence = {output.confidence.calibrated_confidence}%")
    
    def test_incomplete_information_query(self):
        """Test query with missing critical information"""
        query = "Am I eligible for government schemes?"
        
        output = self.council.process_query(query, verbose=False)
        
        # Should have low confidence
        self.assertLess(output.confidence.calibrated_confidence, 40)
        
        # Should flag as unsafe
        self.assertEqual(output.decision.safety_flag, SafetyFlag.UNSAFE_TO_ANSWER.value)
        
        # Should have many unknowns
        self.assertGreater(len(output.unknown_detection.missing_information), 3)
        
        print(f"\n✓ Incomplete info test: Confidence = {output.confidence.calibrated_confidence}%, Unknowns = {len(output.unknown_detection.missing_information)}")
    
    def test_ambiguous_query(self):
        """Test query with ambiguous information"""
        query = "I'm around 30 years old, earn maybe 5-6 lakhs, from somewhere in North India"
        
        output = self.council.process_query(query, verbose=False)
        
        # Should detect ambiguities
        self.assertGreater(len(output.query_processor.ambiguity_flags), 0)
        
        # Should be cautious
        self.assertIn(output.decision.safety_flag, [
            SafetyFlag.ANSWER_WITH_CAUTION.value,
            SafetyFlag.UNSAFE_TO_ANSWER.value
        ])
        
        print(f"\n✓ Ambiguous query test: Ambiguities = {len(output.query_processor.ambiguity_flags)}")
    
    def test_domain_detection(self):
        """Test domain detection"""
        queries = {
            "Am I eligible for PM Kisan scheme?": "government_scheme",
            "What are my tax obligations?": "financial_compliance",
            "Can I file a case for this?": "legal_prescreening"
        }
        
        for query, expected_domain in queries.items():
            output = self.council.process_query(query, verbose=False)
            self.assertEqual(output.domain, expected_domain)
            print(f"✓ Domain '{expected_domain}' detected correctly")

if __name__ == '__main__':
    unittest.main()
