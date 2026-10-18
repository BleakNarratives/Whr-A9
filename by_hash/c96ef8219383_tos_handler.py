from typing import Dict
from datetime import datetime

class TOSHandler:
    def __init__(self):
        self.required_sections = [
            'service_description',
            'user_rights_responsibilities',
            'privacy_policy',
            'termination_conditions',
            'liability_limitations'
        ]

    async def validate_tos_structure(self, tos_document: Dict) -> Dict:
        """Validate the structure and completeness of TOS document."""
        missing_sections = [
            section for section in self.required_sections
            if section not in tos_document
        ]
        return {
            'is_valid': len(missing_sections) == 0,
            'missing_sections': missing_sections,
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    async def generate_tos_template(self, company_info: Dict) -> Dict:
        """Generate a customized TOS template based on company information."""
        return {
            'template_sections': self.required_sections,
            'company_specific_terms': [
                f"Service owner: {company_info.get('company_name', 'Unknown')}",
                f"Service name: {company_info.get('product_name', 'Unnamed Product')}"
            ],
            'generation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    async def analyze_compliance(self, tos_document: Dict) -> Dict:
        """Analyze TOS compliance with legal requirements and best practices."""
        missing = [section for section in self.required_sections if section not in tos_document]
        return {
            'compliance_status': 'non-compliant' if missing else 'compliant',
            'recommendations': [
                'Add missing TOS sections.',
                'Review privacy policy linkage.',
                'Validate termination and liability clauses.'
            ],
            'risk_assessment': {
                'missing_section_count': len(missing),
                'missing_sections': missing
            },
            'analysis_timestamp': datetime.utcnow().isoformat() + 'Z'
        }
