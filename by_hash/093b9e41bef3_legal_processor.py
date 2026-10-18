from typing import Dict, List
from datetime import datetime
import re

class LegalDocumentProcessor:
    def __init__(self):
        self.supported_document_types = ['contract', 'tos', 'privacy_policy', 'disclaimer']
        self.keywords = [
            'privacy', ' data ', 'consent', 'tracking', 'location', 'liability', 'security', 'third-party', 'sdk'
        ]
        self.risk_indicators = [
            'without prior notice', 'waive', 'not liable', 'automatic renewal', 'tracking', 'data sale'
        ]

    async def analyze_document(self, document: Dict) -> Dict:
        """Analyze legal documents for key terms, risks, and compliance issues."""
        text = self._normalize_text(document.get('text', ''))
        return {
            'document_type': self._detect_document_type(text),
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z',
            'key_terms': self._extract_keywords(text),
            'risk_factors': self._detect_risk_indicators(text),
            'compliance_status': self._estimate_compliance_status(text),
            'summary': self._generate_summary(text),
        }

    async def validate_compliance(self, document: Dict) -> Dict:
        """Validate document compliance with legal requirements."""
        text = self._normalize_text(document.get('text', ''))
        issues = []
        if 'privacy' not in text and 'data' not in text:
            issues.append('Privacy and data handling are not clearly described.')
        if 'consent' not in text and 'opt-in' not in text:
            issues.append('Consent or opt-in language is not present.')
        if 'third-party' not in text and 'sdk' not in text:
            issues.append('Third-party SDK or service disclosure is missing.')
        return {
            'is_compliant': len(issues) == 0,
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z',
            'compliance_details': issues,
            'required_actions': [
                'Add explicit data usage language.',
                'Document consent flows clearly.',
                'Include third-party service disclosures.'
            ] if issues else []
        }

    async def generate_summary(self, document: Dict) -> Dict:
        """Generate a human-readable summary of a legal document."""
        text = self._normalize_text(document.get('text', ''))
        return {
            'summary': self._generate_summary(text),
            'key_points': self._extract_keywords(text),
            'generation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _normalize_text(self, text: str) -> str:
        return re.sub(r'\s+', ' ', text.strip().lower())

    def _detect_document_type(self, text: str) -> str:
        if 'terms of service' in text or 'tos' in text:
            return 'terms_of_service'
        if 'privacy policy' in text or 'data collection' in text:
            return 'privacy_policy'
        if 'disclaimer' in text:
            return 'disclaimer'
        return 'legal_document'

    def _extract_keywords(self, text: str) -> List[str]:
        return [keyword.strip() for keyword in self.keywords if keyword.strip() in text]

    def _detect_risk_indicators(self, text: str) -> List[str]:
        return [indicator for indicator in self.risk_indicators if indicator in text]

    def _estimate_compliance_status(self, text: str) -> str:
        issues = self._detect_risk_indicators(text)
        return 'high-risk' if issues else 'review-needed'

    def _generate_summary(self, text: str) -> str:
        sentences = [sentence.strip() for sentence in text.split('.') if sentence.strip()]
        return ' '.join(sentences[:3])
