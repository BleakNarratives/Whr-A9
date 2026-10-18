from typing import Dict, List
from datetime import datetime

class GooglePlayComplianceChecker:
    """Google Play Store compliance checker for Android apps."""

    def __init__(self):
        self.required_permissions = [
            'internet', 'location', 'camera', 'microphone', 'storage'
        ]
        self.prohibited_content = [
            'malware', 'spyware', 'phishing', 'illegal content', 'hate speech'
        ]
        self.privacy_requirements = [
            'data_collection_disclosure', 'third_party_sharing', 'user_consent',
            'data_deletion', 'age_restrictions', 'family_policy_compliance'
        ]

    async def check_app_compliance(self, app_info: Dict) -> Dict:
        """Check Android app compliance with Google Play Store policies."""
        issues = []
        warnings = []

        # Check permissions
        permissions = app_info.get('permissions', [])
        for perm in permissions:
            if perm not in self.required_permissions and 'dangerous' in perm.lower():
                warnings.append(f"Potentially dangerous permission: {perm}")

        # Check content rating
        content_rating = app_info.get('content_rating', '')
        if not content_rating:
            issues.append("Content rating not specified")

        # Check privacy policy
        privacy_policy = app_info.get('privacy_policy', '')
        if not privacy_policy:
            issues.append("Privacy policy required for Google Play Store")
        else:
            privacy_issues = self._check_privacy_compliance(privacy_policy)
            issues.extend(privacy_issues)

        # Check target SDK
        target_sdk = app_info.get('target_sdk_version', 0)
        if target_sdk < 30:  # Android 11
            warnings.append("Target SDK version should be 30+ for Android 11+ features")

        return {
            'platform': 'google_play_store',
            'is_compliant': len(issues) == 0,
            'critical_issues': issues,
            'warnings': warnings,
            'recommendations': self._generate_recommendations(issues, warnings),
            'check_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    async def validate_privacy_policy(self, privacy_policy: Dict) -> Dict:
        """Validate privacy policy against Google Play requirements."""
        issues = []

        required_sections = [
            'data_collection', 'data_usage', 'data_sharing', 'user_rights',
            'contact_information', 'updates'
        ]

        for section in required_sections:
            if section not in privacy_policy:
                issues.append(f"Missing required section: {section}")

        # Check for GDPR compliance indicators
        policy_text = privacy_policy.get('text', '').lower()
        if 'gdpr' not in policy_text and 'general data protection regulation' not in policy_text:
            issues.append("GDPR compliance not mentioned")

        return {
            'is_valid': len(issues) == 0,
            'validation_issues': issues,
            'compliance_level': 'high' if len(issues) == 0 else 'medium' if len(issues) <= 2 else 'low',
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _check_privacy_compliance(self, privacy_policy: str) -> List[str]:
        """Check privacy policy text for compliance issues."""
        issues = []
        text = privacy_policy.lower()

        if 'data collection' not in text:
            issues.append("Data collection practices not disclosed")
        if 'third party' not in text and 'third-party' not in text:
            issues.append("Third-party data sharing not addressed")
        if 'consent' not in text:
            issues.append("User consent mechanisms not described")
        if 'delete' not in text and 'removal' not in text:
            issues.append("Data deletion rights not mentioned")

        return issues

    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate recommendations based on issues and warnings."""
        recommendations = []

        if any('privacy' in issue.lower() for issue in issues):
            recommendations.append("Update privacy policy to include all required disclosures")
        if any('permission' in warning.lower() for warning in warnings):
            recommendations.append("Review and justify dangerous permissions in manifest")
        if any('sdk' in str(issues + warnings).lower()):
            recommendations.append("Ensure target SDK is 30+ and app is compatible with latest Android versions")

        return recommendations or ["Review Google Play Store policies regularly"]
