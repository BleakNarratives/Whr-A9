#!/usr/bin/env python3
"""EquiLex CLI for Android developer compliance, legal templates, and wrapper scaffolding."""
import argparse
import json
import re
import asyncio
from datetime import datetime
from pathlib import Path
from textwrap import dedent

# Import compliance checkers
try:
    from backend.services.google_play_compliance import GooglePlayComplianceChecker
    from backend.services.apple_appstore_compliance import AppleAppStoreComplianceChecker
except ImportError:
    # Fallback for when running without full backend
    GooglePlayComplianceChecker = None
    AppleAppStoreComplianceChecker = None

class EquiLexCore:
    def __init__(self):
        self.templates = {
            "privacy_policy": self._privacy_policy_template,
            "tos": self._tos_template,
            "disclaimer": self._disclaimer_template,
        }
        self.android_play_checklist = [
            "Privacy Policy URL",
            "Data Collection Disclosure",
            "User Consent Flow",
            "Location Permission Justification",
            "Personal Data Handling",
            "Third-Party SDK Notice",
            "Security & Encryption",
            "Accessibility Statement",
            "Age Restriction Compliance",
        ]

    def analyze_text(self, text: str) -> dict:
        cleaned = self._normalize_text(text)
        terms = self._extract_keywords(cleaned)
        risk = self._find_risks(cleaned)
        summary = self._generate_summary(cleaned)
        return {
            "document_type": self._guess_document_type(cleaned),
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "key_terms": terms,
            "risk_factors": risk,
            "summary": summary,
            "compliance_status": "pending",
        }

    def generate_template(self, template_type: str, company_name: str, product_name: str, jurisdiction: str) -> dict:
        generator = self.templates.get(template_type)
        if not generator:
            raise ValueError(f"Unknown template type: {template_type}")
        return generator(company_name, product_name, jurisdiction)

    def validate_tos_structure(self, document: dict) -> dict:
        required = [
            "service_description",
            "user_rights_responsibilities",
            "privacy_policy",
            "termination_conditions",
            "liability_limitations",
        ]
        missing = [field for field in required if field not in document]
        return {
            "is_valid": len(missing) == 0,
            "missing_sections": missing,
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def android_compliance_check(self, privacy_text: str, app_label: str, package_name: str) -> dict:
        privacy = self._normalize_text(privacy_text)
        issues = []
        if "location" not in privacy and "gps" not in privacy:
            issues.append("No location permission justification found.")
        if "data" not in privacy and "collect" not in privacy:
            issues.append("No explicit data collection disclosure.")
        if "third-party" not in privacy and "sdk" not in privacy:
            issues.append("Third-party SDK usage disclosure is missing.")
        if "consent" not in privacy and "permission" not in privacy:
            issues.append("User consent flow is not described clearly.")
        return {
            "app_label": app_label,
            "package_name": package_name,
            "android_play_checklist": self.android_play_checklist,
            "issues_found": issues,
            "recommendations": [
                "Add explicit privacy and data usage sections for every permission.",
                "Document third-party SDK telemetry clearly.",
                "Attach a user-facing consent flow in the app.",
            ],
            "review_timestamp": datetime.utcnow().isoformat() + "Z",
        }

    def generate_webview_wrapper_snippet(self, app_package: str, destination: str = "android") -> dict:
        if destination == "android":
            code = dedent(f"""
                <!-- Android webview wrapper snippet -->
                <WebView
                    android:id=\"@+id/equilexWebView\"
                    android:layout_width=\"match_parent\"
                    android:layout_height=\"match_parent\"
                    android:usesCleartextTraffic=\"true\" />

                // In your Android Activity
                val webView = findViewById<WebView>(R.id.equilexWebView)
                webView.settings.javaScriptEnabled = true
                webView.loadUrl(\"https://your-wrapper-host.example.com?app={app_package}\")
            """)
        else:
            code = dedent(f"""
                <!-- Generic web wrapper -->
                <iframe src=\"https://your-wrapper-host.example.com?app={app_package}\" width=\"100%\" height=\"100%\"></iframe>
            """)
        return {
            "target": destination,
            "app_package": app_package,
            "snippet": code,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    def create_force_multiplier(self, report: dict) -> dict:
        multiplier = {
            "next_steps": [
                "Add EquiLex metadata to your Android app manifest.",
                "Use generated templates as a starting compliance scaffold.",
                "Automate privacy policy regeneration when SDKs change.",
                "Expose a developer checklist inside your GitHub repo.",
            ],
            "productivity_boosters": [
                "Use Copilot prompts that reference EquiLex templates.",
                "Ship legal checklist issues as GitHub issues from Termux.",
                "Expose CLI commands in VS Code via the extension scaffold.",
            ],
            "summary": report,
        }
        return multiplier

    def _guess_document_type(self, text: str) -> str:
        if "terms of service" in text.lower() or "tos" in text.lower():
            return "terms_of_service"
        if "privacy policy" in text.lower() or "data collection" in text.lower():
            return "privacy_policy"
        return "general_legal_document"

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip()).lower()

    def _extract_keywords(self, text: str) -> list:
        keywords = [
            "privacy",
            "data",
            "consent",
            "tracking",
            "location",
            "liability",
            "user rights",
            "third-party",
        ]
        return [term for term in keywords if term in text]

    def _find_risks(self, text: str) -> list:
        risks = []
        if "without prior notice" in text:
            risks.append("Contains one-way modification clause.")
        if "waive" in text and "liability" in text:
            risks.append("Potentially broad liability waiver.")
        if "tracking" in text and "consent" not in text:
            risks.append("Tracking described without consent flow.")
        if "automatic renewal" in text and "cancel" not in text:
            risks.append("Auto-renewal terms may be missing cancellation details.")
        return risks

    def _generate_summary(self, text: str) -> str:
        lines = [line.strip() for line in text.split(".") if line.strip()]
        return " ".join(lines[:3])

    def _privacy_policy_template(self, company_name: str, product_name: str, jurisdiction: str) -> dict:
        return {
            "type": "privacy_policy",
            "company_name": company_name,
            "product_name": product_name,
            "jurisdiction": jurisdiction,
            "content": dedent(f"""
                {company_name} respects your privacy.

                1. Introduction
                {product_name} collects personal data only as needed to deliver core mobile functionality.

                2. Data Collected
                We may collect device identifiers, location data, analytics events, and diagnostic logs.

                3. How Data Is Used
                Data is used to improve the app, personalize experience, and enable essential services.

                4. Third-Party Services
                Third-party SDKs may collect telemetry and analytics. We disclose all partners in the app documentation.

                5. User Rights
                Users may request data deletion, access, or correction in accordance with {jurisdiction} rules.

                6. Contact
                Contact privacy@{company_name.lower().replace(' ', '')}.com for questions.
            """),
        }

    def _tos_template(self, company_name: str, product_name: str, jurisdiction: str) -> dict:
        return {
            "type": "terms_of_service",
            "company_name": company_name,
            "product_name": product_name,
            "jurisdiction": jurisdiction,
            "content": dedent(f"""
                1. Service Description
                {product_name} is a mobile-first application for Android developers and legal compliance.

                2. User Rights and Responsibilities
                Users agree to use the service lawfully and not to reverse engineer or misuse the app.

                3. Privacy
                User privacy is protected by our Privacy Policy, which is a separate legal document.

                4. Termination
                We may suspend or terminate access for policy or security reasons.

                5. Liability
                {company_name} is not liable for indirect damages, except as required by {jurisdiction} law.
            """),
        }

    def _disclaimer_template(self, company_name: str, product_name: str, jurisdiction: str) -> dict:
        return {
            "type": "disclaimer",
            "company_name": company_name,
            "product_name": product_name,
            "jurisdiction": jurisdiction,
            "content": dedent(f"""
                This is not legal advice. The information provided for {product_name} is for general guidance only.
                For specific legal advice, consult a licensed attorney in {jurisdiction}.
            """),
        }


def load_text_input(source: str | None) -> str:
    if source is None or source == "-":
        return sys.stdin.read()
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return source


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EquiLex CLI for Android legal compliance and wrapper generation.")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze a legal document or policy text.")
    analyze.add_argument("source", nargs="?", default="-", help="File path or raw text. Defaults to stdin.")
    analyze.add_argument("--format", choices=["json", "text"], default="json")

    generate = sub.add_parser("generate", help="Generate a legal template.")
    generate.add_argument("template", choices=["privacy_policy", "tos", "disclaimer"], help="Template type.")
    generate.add_argument("--company", required=True, help="Company or project name.")
    generate.add_argument("--product", required=True, help="Product name.")
    generate.add_argument("--jurisdiction", default="Global", help="Applicable jurisdiction.")
    generate.add_argument("--format", choices=["json", "text"], default="json")

    validate = sub.add_parser("validate", help="Validate a TOS structure or Android compliance text.")
    validate.add_argument("source", nargs="?", default="-", help="TOS document path, JSON object, or raw text.")
    validate.add_argument("--mode", choices=["tos", "android"], default="tos")
    validate.add_argument("--package", default="com.example.app", help="Android package name for android mode.")
    validate.add_argument("--label", default="Example App", help="App label for android mode.")
    validate.add_argument("--format", choices=["json", "text"], default="json")

    snippet = sub.add_parser("snippet", help="Generate a wrapper snippet for Android or generic web.")
    snippet.add_argument("--package", default="com.example.app", help="App package or wrapper ID.")
    snippet.add_argument("--target", choices=["android", "web"], default="android")
    snippet.add_argument("--format", choices=["json", "text"], default="text")

    multiplier = sub.add_parser("force-multiplier", help="Create a force multiplier plan for the current output.")
    multiplier.add_argument("--source", nargs="?", default="-", help="Optional existing report JSON or raw text source.")
    multiplier.add_argument("--format", choices=["json", "text"], default="json")

    # Google Play Store compliance
    play_store = sub.add_parser("play-store", help="Check Google Play Store compliance for Android apps.")
    play_store.add_argument("app_info", help="JSON file or string with app information.")
    play_store.add_argument("--format", choices=["json", "text"], default="json")

    # Apple App Store compliance
    app_store = sub.add_parser("app-store", help="Check Apple App Store compliance for iOS apps.")
    app_store.add_argument("app_info", help="JSON file or string with app information.")
    app_store.add_argument("--format", choices=["json", "text"], default="json")

    return parser


def format_output(payload: dict | str, format_type: str) -> str:
    if format_type == "json":
        return json.dumps(payload, indent=2, ensure_ascii=False)
    if isinstance(payload, dict):
        lines = [f"{key}: {value}" for key, value in payload.items()]
        return "\n".join(lines)
    return str(payload)


async def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    core = EquiLexCore()

    if args.command == "analyze":
        text = load_text_input(args.source)
        output = core.analyze_text(text)
    elif args.command == "generate":
        output = core.generate_template(args.template, args.company, args.product, args.jurisdiction)
    elif args.command == "validate":
        payload = load_text_input(args.source)
        if args.mode == "tos":
            try:
                document = json.loads(payload)
            except json.JSONDecodeError:
                document = {"raw_text": payload}
            output = core.validate_tos_structure(document)
        else:
            output = core.android_compliance_check(payload, args.label, args.package)
    elif args.command == "snippet":
        output = core.generate_webview_wrapper_snippet(args.package, args.target)
    elif args.command == "force-multiplier":
        payload = load_text_input(args.source)
        try:
            report = json.loads(payload)
        except json.JSONDecodeError:
            report = {"source": payload[:1024]}
        output = core.create_force_multiplier(report)
    elif args.command == "play-store":
        if GooglePlayComplianceChecker is None:
            output = {"error": "Google Play compliance checker not available"}
        else:
            payload = load_text_input(args.app_info)
            try:
                app_info = json.loads(payload)
            except json.JSONDecodeError:
                output = {"error": "Invalid JSON format for app info"}
            else:
                checker = GooglePlayComplianceChecker()
                output = await checker.check_app_compliance(app_info)
    elif args.command == "app-store":
        if AppleAppStoreComplianceChecker is None:
            output = {"error": "Apple App Store compliance checker not available"}
        else:
            payload = load_text_input(args.app_info)
            try:
                app_info = json.loads(payload)
            except json.JSONDecodeError:
                output = {"error": "Invalid JSON format for app info"}
            else:
                checker = AppleAppStoreComplianceChecker()
                output = await checker.check_app_compliance(app_info)
    else:
        parser.print_help()
        return 1

    print(format_output(output, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
