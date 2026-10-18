from typing import Dict, List
from datetime import datetime

class AppleAppStoreComplianceChecker:
    """Apple App Store compliance checker for iOS apps."""

    def __init__(self):
        self.required_sections = [
            'app_store_review_guidelines', 'human_interface_guidelines',
            'privacy_manifest', 'app_tracking_transparency', 'sign_in_with_apple'
        ]
        self.prohibited_behaviors = [
            'unauthorized_purchases', 'excessive_data_collection', 'deceptive_practices',
            'malware', 'inappropriate_content', 'unfair_competition'
        ]
        self.privacy_requirements = [
            'privacy_manifest', 'app_tracking_transparency', 'data_collection_disclosure',
            'purpose_strings', 'user_consent', 'data_minimization'
        ]

    async def check_app_compliance(self, app_info: Dict) -> Dict:
        """Check iOS app compliance with Apple App Store policies."""
        issues = []
        warnings = []

        # Check app review guidelines compliance
        review_status = app_info.get('app_review_status', '')
        if review_status == 'rejected':
            issues.append("App has been rejected by App Review")

        # Check privacy manifest
        privacy_manifest = app_info.get('privacy_manifest', {})
        if not privacy_manifest:
            issues.append("Privacy manifest required for iOS apps")
        else:
            manifest_issues = self._validate_privacy_manifest(privacy_manifest)
            issues.extend(manifest_issues)

        # Check App Tracking Transparency
        tracking_enabled = app_info.get('app_tracking_transparency', False)
        if not tracking_enabled and app_info.get('uses_tracking', False):
            issues.append("App Tracking Transparency required for apps using tracking")

        # Check Sign in with Apple availability
        sign_in_apple = app_info.get('sign_in_with_apple', False)
        if not sign_in_apple:
            warnings.append("Consider implementing Sign in with Apple for better user experience")

        # Check minimum iOS version
        min_ios_version = app_info.get('minimum_ios_version', '0')
        if float(min_ios_version) < 15.0:
            warnings.append("Minimum iOS version should be 15.0+ for latest features")

        # Check for prohibited APIs
        used_apis = app_info.get('used_apis', [])
        prohibited_apis = ['private_apis', 'undocumented_apis']
        for api in used_apis:
            if api in prohibited_apis:
                issues.append(f"Prohibited API usage: {api}")

        return {
            'platform': 'apple_app_store',
            'is_compliant': len(issues) == 0,
            'critical_issues': issues,
            'warnings': warnings,
            'recommendations': self._generate_recommendations(issues, warnings),
            'check_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    async def validate_privacy_manifest(self, privacy_manifest: Dict) -> Dict:
        """Validate privacy manifest against Apple requirements."""
        issues = []

        required_keys = [
            'NSPrivacyCollectedDataTypes', 'NSPrivacyAccessedAPITypes',
            'NSPrivacyTracking', 'NSPrivacyTrackingDomains'
        ]

        for key in required_keys:
            if key not in privacy_manifest:
                issues.append(f"Missing required privacy manifest key: {key}")

        # Check data types
        collected_data = privacy_manifest.get('NSPrivacyCollectedDataTypes', [])
        if not collected_data:
            issues.append("No data collection types specified in privacy manifest")

        # Check API usage
        accessed_apis = privacy_manifest.get('NSPrivacyAccessedAPITypes', [])
        if accessed_apis and not all('NSPrivacyAccessedAPIType' in api for api in accessed_apis):
            issues.append("API access types not properly categorized")

        return {
            'is_valid': len(issues) == 0,
            'validation_issues': issues,
            'compliance_level': 'high' if len(issues) == 0 else 'medium' if len(issues) <= 2 else 'low',
            'validation_timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _validate_privacy_manifest(self, manifest: Dict) -> List[str]:
        """Internal validation of privacy manifest."""
        issues = []

        if 'NSPrivacyCollectedDataTypes' not in manifest:
            issues.append("Missing NSPrivacyCollectedDataTypes")
        if 'NSPrivacyTracking' not in manifest:
            issues.append("Missing NSPrivacyTracking declaration")

        return issues

    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate recommendations based on issues and warnings."""
        recommendations = []

        if any('privacy' in issue.lower() for issue in issues):
            recommendations.append("Update privacy manifest with all required data types and API usage")
        if any('tracking' in issue.lower() for issue in issues):
            recommendations.append("Implement App Tracking Transparency framework")
        if any('ios' in str(warnings).lower()):
            recommendations.append("Update minimum iOS version to 15.0+")

        return recommendations or ["Review Apple App Store Review Guidelines regularly"]
