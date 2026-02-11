"""
Query Processor Agent - Extracts structured entities from natural language
"""
import re
from typing import List
from agents.base_agent import BaseAgent
from core.schemas import (
    QueryProcessorOutput, QueryEntities, Domain, Category
)

class QueryProcessorAgent(BaseAgent):
    """
    Agent 1: Query Processor / Pre-Parsing Agent
    Cleans user's natural-language question and extracts structured fields
    """
    
    SCHEME_KEYWORDS = ['scheme', 'yojana', 'subsidy', 'grant', 'benefit', 'eligibility']
    LEGAL_KEYWORDS = ['legal', 'law', 'court', 'case', 'advocate', 'rights']
    FINANCIAL_KEYWORDS = ['tax', 'loan', 'investment', 'finance', 'banking', 'gst']
    
    STATES_UT = [
        'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar', 'chhattisgarh',
        'goa', 'gujarat', 'haryana', 'himachal pradesh', 'jharkhand', 'karnataka',
        'kerala', 'madhya pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'punjab', 'rajasthan', 'sikkim', 'tamil nadu',
        'telangana', 'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal',
        'delhi', 'jammu and kashmir', 'ladakh', 'puducherry', 'chandigarh',
        'andaman and nicobar', 'dadra and nagar haveli', 'daman and diu', 'lakshadweep'
    ]
    
    DOCUMENTS = [
        'aadhar', 'aadhaar', 'pan', 'income certificate', 'caste certificate',
        'domicile certificate', 'ration card', 'voter id', 'driving license',
        'passport', 'birth certificate', 'bank statement', 'salary slip'
    ]
    
    def process(self, user_query: str) -> QueryProcessorOutput:
        """Main processing function"""
        self.logger.info("Processing query...")
        
        cleaned = self._clean_query(user_query)
        domain = self._detect_domain(cleaned)
        entities = self._extract_entities(cleaned)
        ambiguity_flags = self._identify_ambiguities(cleaned, entities)
        notes = self._generate_notes(entities, ambiguity_flags)
        
        return QueryProcessorOutput(
            cleaned_query=cleaned,
            detected_domain=domain,
            entities=entities,
            ambiguity_flags=ambiguity_flags,
            notes=notes
        )
    
    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query"""
        cleaned = ' '.join(query.split())
        return cleaned.strip()
    
    def _detect_domain(self, query: str) -> str:
        """Detect the domain of the query"""
        query_lower = query.lower()
        
        scheme_score = sum(1 for kw in self.SCHEME_KEYWORDS if kw in query_lower)
        legal_score = sum(1 for kw in self.LEGAL_KEYWORDS if kw in query_lower)
        financial_score = sum(1 for kw in self.FINANCIAL_KEYWORDS if kw in query_lower)
        
        max_score = max(scheme_score, legal_score, financial_score)
        
        if max_score == 0:
            return Domain.OTHER.value
        elif scheme_score == max_score:
            return Domain.GOVERNMENT_SCHEME.value
        elif legal_score == max_score:
            return Domain.LEGAL_PRESCREENING.value
        else:
            return Domain.FINANCIAL_COMPLIANCE.value
    
    def _extract_entities(self, query: str) -> QueryEntities:
        """Extract structured entities from query"""
        query_lower = query.lower()
        entities = QueryEntities()
        
        # Extract age
        age_patterns = [
            r'\b(\d{1,2})\s*(?:years?|yrs?)\s*old\b',
            r'\bage\s*(?:is\s*)?(\d{1,2})\b',
            r'\b(\d{1,2})\s*(?:year|yr)\b'
        ]
        for pattern in age_patterns:
            match = re.search(pattern, query_lower)
            if match:
                entities.age = int(match.group(1))
                break
        
        # Extract income
        income_patterns = [
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:lpa|lakhs?\s*per\s*annum)',
            r'annual\s*income\s*(?:of\s*)?(?:rs\.?\s*)?(\d+(?:,\d+)*)',
            r'monthly\s*income\s*(?:of\s*)?(?:rs\.?\s*)?(\d+(?:,\d+)*)',
            r'(?:earn|earning|salary)\s*(?:of\s*)?(?:rs\.?\s*)?(\d+(?:,\d+)*)'
        ]
        
        for pattern in income_patterns:
            match = re.search(pattern, query_lower)
            if match:
                income_str = match.group(1).replace(',', '')
                income_val = float(income_str)
                
                if 'lpa' in match.group(0) or 'lakhs per annum' in match.group(0):
                    entities.annual_income = income_val * 100000
                elif 'annual' in match.group(0):
                    entities.annual_income = income_val
                elif 'monthly' in match.group(0):
                    entities.monthly_income = income_val
                    entities.annual_income = income_val * 12
                break
        
        # Extract state
        for state in self.STATES_UT:
            if state in query_lower:
                entities.state_or_ut = state.title()
                break
        
        # Extract category
        for cat in Category:
            if cat.value.lower() in query_lower:
                entities.category = cat.value
                break
        
        # Extract occupation
        occupation_patterns = [
            r'(?:work\s*as\s*a?\s*)(\w+)',
            r'(?:occupation\s*(?:is\s*)?)(\w+)',
            r'(?:job\s*(?:is\s*)?)(\w+)',
            r'\b(farmer|student|teacher|engineer|doctor|labor|labourer)\b'
        ]
        for pattern in occupation_patterns:
            match = re.search(pattern, query_lower)
            if match:
                entities.occupation = match.group(1).capitalize()
                break
        
        # Extract documents
        for doc in self.DOCUMENTS:
            if doc in query_lower:
                entities.documents_mentioned.append(doc.title())
        
        return entities
    
    def _identify_ambiguities(self, query: str, entities: QueryEntities) -> List[str]:
        """Identify ambiguities in the query"""
        flags = []
        
        if entities.age is None:
            flags.append("Age not specified")
        
        if entities.annual_income is None and entities.monthly_income is None:
            flags.append("Income information missing")
        
        if entities.state_or_ut is None:
            flags.append("State/UT not mentioned (may affect scheme eligibility)")
        
        if entities.category is None:
            flags.append("Caste category not specified")
        
        vague_terms = ['maybe', 'approximately', 'around', 'roughly', 'about', 'i think']
        if any(term in query.lower() for term in vague_terms):
            flags.append("Query contains uncertainty markers (maybe, approximately, etc.)")
        
        return flags
    
    def _generate_notes(self, entities: QueryEntities, ambiguity_flags: List[str]) -> str:
        """Generate explanatory notes"""
        extracted_count = sum([
            entities.age is not None,
            entities.annual_income is not None,
            entities.state_or_ut is not None,
            entities.category is not None,
            entities.occupation is not None,
            len(entities.documents_mentioned) > 0
        ])
        
        if extracted_count >= 4:
            return f"Successfully extracted {extracted_count}/6 key entities. Query is relatively clear."
        elif extracted_count >= 2:
            return f"Extracted {extracted_count}/6 key entities. Several critical fields missing. {len(ambiguity_flags)} ambiguities detected."
        else:
            return f"Only extracted {extracted_count}/6 key entities. Query is highly ambiguous with insufficient information."
