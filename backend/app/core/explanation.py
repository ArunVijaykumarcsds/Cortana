"""
CORTANA — Safe Deterministic-First AI Explanation Service.
Translates pre-computed ML inference facts into plain-English risk narratives.
Strictly prohibits LLMs from generating or altering scores/decisions.
"""

import json
import os
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

from backend.app.schemas.explanation import (
    ExplanationFacts,
    ExplanationResponse,
    TriggeredRuleFact,
)

RULE_FRIENDLY_NAMES: Dict[str, str] = {
    "HIGH_AMOUNT": "High Amount Anomaly",
    "ORIGIN_BALANCE_INCONSISTENCY": "Origin Balance Inconsistency",
    "DESTINATION_BALANCE_INCONSISTENCY": "Destination Balance Inconsistency",
    "LARGE_BALANCE_CHANGE": "Large Rapid Balance Drain",
    "HIGH_RISK_TRANSACTION_TYPE": "High-Risk Transaction Type (TRANSFER/CASH_OUT)",
    "ZERO_BALANCE_ANOMALY": "Zero-Balance Anomaly",
}


class DeterministicExplanationEngine:
    """
    Mandatory deterministic template generator.
    Works offline with zero external API keys. Produces grounded, consistent explanations.
    """

    def generate(self, facts: ExplanationFacts) -> ExplanationResponse:
        signals: List[str] = []
        sentences: List[str] = []

        # 1. Decision and baseline risk level
        pct_score = f"{facts.fused_risk_score * 100:.1f}%"
        sentences.append(
            f"Transaction {facts.transaction_id} was evaluated as {facts.risk_level} risk "
            f"with a fused risk score of {pct_score}, resulting in an automated {facts.decision} decision."
        )

        # 2. Context-specific signal elaboration
        if facts.dataset_context == "PaySim":
            signals.append("Model 1 (Random Forest)")
            m1_prob = facts.model_1_probability if facts.model_1_probability is not None else 0.0
            sentences.append(
                f"In the PaySim mobile banking context, Model 1 (Random Forest supervised classifier) "
                f"assigned a calibrated fraud probability of {m1_prob * 100:.1f}% (weight: 80%)."
            )

            if facts.triggered_rules:
                signals.append("Rules Engine")
                rule_names = []
                for r in facts.triggered_rules:
                    friendly = r.label or RULE_FRIENDLY_NAMES.get(r.rule_key, r.rule_key)
                    rule_names.append(friendly)
                    signals.append(f"Rule: {r.rule_key}")

                joined_rules = ", ".join(rule_names)
                sentences.append(
                    f"The Behavioral Rules Engine (weight: 10%) triggered {len(facts.triggered_rules)} rule(s): {joined_rules}. "
                    f"These rules flag structural balance inconsistencies and atypical transfer patterns."
                )
            else:
                sentences.append("No behavioral rules were triggered for this transaction.")

        elif facts.dataset_context == "ULB":
            signals.append("Model 2 (Isolation Forest)")
            m2_score = facts.model_2_anomaly_score if facts.model_2_anomaly_score is not None else 0.0
            sentences.append(
                f"In the ULB credit card context, Model 2 (Isolation Forest unsupervised anomaly detector) "
                f"assigned a calibrated anomaly score of {m2_score * 100:.1f}% based on continuous PCA feature deviations (weight: 100%)."
            )

        # 3. Recommended analyst guidance
        if facts.decision == "REVIEW" or facts.risk_level in ("HIGH", "CRITICAL"):
            sentences.append(
                "Because the fused score meets or exceeds the critical review threshold (98%), "
                "this transaction has been queued for human analyst review to verify customer authorization."
            )
        else:
            sentences.append(
                "The fused risk is below the review threshold; automated processing allowed this transaction to PASS."
            )

        full_text = " ".join(sentences)

        return ExplanationResponse(
            transaction_id=facts.transaction_id,
            risk_level=facts.risk_level,
            decision=facts.decision,
            fused_risk_score=facts.fused_risk_score,
            explanation_text=full_text,
            referenced_signals=signals,
            provider="deterministic_fallback",
            is_fallback=True,
        )


class ExplanationService:
    """
    Unified Explanation Service orchestrating optional external LLM generation
    with guaranteed deterministic fallback and Medium+ invocation policy.
    """

    def __init__(self, fallback_engine: Optional[DeterministicExplanationEngine] = None):
        self.fallback_engine = fallback_engine or DeterministicExplanationEngine()
        self.llm_provider = os.getenv("CORTANA_LLM_PROVIDER", "").lower().strip()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    def generate_explanation(self, facts: ExplanationFacts) -> ExplanationResponse:
        """
        Generates an explanation for the given pre-computed facts.
        LOW-risk transactions or missing API credentials immediately use deterministic fallback.
        """
        # Medium+ Policy: LOW risk uses fast deterministic generator
        if facts.risk_level == "LOW":
            return self.fallback_engine.generate(facts)

        # Check if external LLM provider is configured
        if not self.gemini_key and not self.openai_key and not self.llm_provider:
            return self.fallback_engine.generate(facts)

        try:
            # Attempt LLM generation
            llm_result = self._call_llm_provider(facts)
            if llm_result:
                return llm_result
        except Exception:
            # Any provider failure gracefully falls back
            pass

        return self.fallback_engine.generate(facts)

    def _call_llm_provider(self, facts: ExplanationFacts) -> Optional[ExplanationResponse]:
        """
        Calls configured LLM provider with structured facts only.
        Validates returned signals against supplied facts.
        """
        # Allowed signal whitelist from facts
        allowed_signals = ["Model 1 (Random Forest)", "Model 2 (Isolation Forest)", "Rules Engine"]
        for r in facts.triggered_rules:
            allowed_signals.append(f"Rule: {r.rule_key}")
            allowed_signals.append(r.rule_key)
            if r.label:
                allowed_signals.append(r.label)

        # Prepare structured prompt facts (NO PII, NO Raw Payload)
        prompt_data = {
            "transaction_id": facts.transaction_id,
            "dataset_context": facts.dataset_context,
            "type": facts.type,
            "risk_level": facts.risk_level,
            "decision": facts.decision,
            "fused_risk_score": f"{facts.fused_risk_score * 100:.1f}%",
            "active_components": facts.active_components,
            "model_1_probability": f"{facts.model_1_probability * 100:.1f}%" if facts.model_1_probability is not None else None,
            "rules_risk_score": f"{facts.rules_risk_score * 100:.1f}%" if facts.rules_risk_score is not None else None,
            "model_2_anomaly_score": f"{facts.model_2_anomaly_score * 100:.1f}%" if facts.model_2_anomaly_score is not None else None,
            "triggered_rules": [
                {"key": r.rule_key, "name": r.label, "severity": r.severity, "desc": r.description}
                for r in facts.triggered_rules
            ],
            "allowed_signal_labels": allowed_signals,
        }

        # If Gemini API Key is available
        if self.gemini_key:
            return self._call_gemini(facts, prompt_data, allowed_signals)

        return None

    def _call_gemini(
        self, facts: ExplanationFacts, prompt_data: Dict[str, Any], allowed_signals: List[str]
    ) -> Optional[ExplanationResponse]:
        """
        Invokes Google Gemini REST API safely using standard library urllib with timeout.
        """
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
            f"?key={self.gemini_key}"
        )
        system_instruction = (
            "You are an explanation-only assistant for CORTANA Financial Risk Intelligence. "
            "You MUST NOT calculate or alter risk scores or decisions. "
            "Explain the deterministic reasons why this transaction was assigned its risk level. "
            "You must return ONLY a JSON object with keys: "
            "'explanation_text' (string, 2-3 concise sentences) and "
            "'referenced_signals' (list of strings chosen strictly from allowed_signal_labels)."
        )

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": json.dumps(prompt_data)}]}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.1,
            },
        }

        req = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(req, timeout=5) as response:
            if response.status != 200:
                return None
            res_body = json.loads(response.read().decode("utf-8"))
            raw_text = res_body["candidates"][0]["content"]["parts"][0]["text"]
            parsed_json = json.loads(raw_text)

            # Validate signals against whitelist
            raw_signals = parsed_json.get("referenced_signals", [])
            valid_signals = [s for s in raw_signals if s in allowed_signals]
            if not valid_signals:
                valid_signals = [s for s in allowed_signals if s.startswith("Model") or s.startswith("Rules")]

            return ExplanationResponse(
                transaction_id=facts.transaction_id,
                risk_level=facts.risk_level,
                decision=facts.decision,
                fused_risk_score=facts.fused_risk_score,
                explanation_text=parsed_json.get("explanation_text", "").strip(),
                referenced_signals=valid_signals,
                provider="gemini",
                is_fallback=False,
            )


def extract_explanation_facts_from_db(
    tx_id: str,
    dataset_context: str,
    tx_type: str,
    risk_level: str,
    decision: str,
    fused_risk: float,
    model_1_prob: Optional[float] = None,
    rules_risk: Optional[float] = None,
    model_2_score: Optional[float] = None,
    triggered_rules_raw: Optional[List[Dict[str, Any]]] = None,
) -> ExplanationFacts:
    """
    Extracts structured facts for explanation without any raw customer PII.
    """
    active_components = ["model_1", "rules"] if dataset_context == "PaySim" else ["model_2"]

    rule_facts: List[TriggeredRuleFact] = []
    if triggered_rules_raw and isinstance(triggered_rules_raw, list):
        for r in triggered_rules_raw:
            if isinstance(r, dict):
                r_key = r.get("rule_key", "UNKNOWN_RULE")
                rule_facts.append(
                    TriggeredRuleFact(
                        rule_key=r_key,
                        label=RULE_FRIENDLY_NAMES.get(r_key, r_key),
                        severity=r.get("severity", "HIGH"),
                        description=r.get("description", "Atypical transaction pattern detected"),
                        field=r.get("field"),
                    )
                )

    return ExplanationFacts(
        transaction_id=tx_id,
        dataset_context=dataset_context,  # type: ignore[arg-type]
        type=tx_type,
        risk_level=risk_level,  # type: ignore[arg-type]
        decision=decision,  # type: ignore[arg-type]
        fused_risk_score=float(fused_risk),
        active_components=active_components,
        model_1_probability=float(model_1_prob) if model_1_prob is not None else None,
        rules_risk_score=float(rules_risk) if rules_risk is not None else None,
        model_2_anomaly_score=float(model_2_score) if model_2_score is not None else None,
        triggered_rules=rule_facts,
    )
