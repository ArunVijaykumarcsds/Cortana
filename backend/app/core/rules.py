"""
CORTANA — Behavioral Rules Engine.
Authoritative implementation of the six behavioral risk rules
defined in rules/risk_rules.json for PaySim transactions.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.inference import RiskLevel, RuleKey, TriggeredRule


class RulesEngine:
    """
    Evaluates PaySim transactions against the six finalized behavioral rules.
    """

    def __init__(self, rules_config_path: Path):
        self.rules_config_path = Path(rules_config_path)
        if not self.rules_config_path.exists():
            raise FileNotFoundError(f"Rules configuration not found at {self.rules_config_path}")

        with open(self.rules_config_path, "r", encoding="utf-8") as f:
            self.rules_definitions = json.load(f)

        # Build lookup table by rule_key
        self.rules_by_key: Dict[str, Dict[str, Any]] = {
            r["rule_key"]: r for r in self.rules_definitions
        }
        
        # Verify 6 expected rules are present
        expected_keys = {
            "HIGH_AMOUNT",
            "ORIGIN_BALANCE_INCONSISTENCY",
            "DESTINATION_BALANCE_INCONSISTENCY",
            "LARGE_BALANCE_CHANGE",
            "HIGH_RISK_TRANSACTION_TYPE",
            "ZERO_BALANCE_ANOMALY",
        }
        actual_keys = set(self.rules_by_key.keys())
        if not expected_keys.issubset(actual_keys):
            raise ValueError(f"Missing expected rules in config: {expected_keys - actual_keys}")

    def evaluate(
        self,
        tx_type: str,
        amount: float,
        origin_balance_before: float,
        origin_balance_after: float,
        destination_balance_before: float,
        destination_balance_after: float,
    ) -> Tuple[List[TriggeredRule], float]:
        """
        Evaluates a PaySim transaction and returns:
        1. List of triggered rules.
        2. Aggregated raw behavioral risk score (sum of weights of triggered enabled rules).
        """
        amount = float(amount)
        old_org = float(origin_balance_before)
        new_org = float(origin_balance_after)
        old_dest = float(destination_balance_before)
        new_dest = float(destination_balance_after)
        tx_type_upper = str(tx_type).upper()

        triggered: List[TriggeredRule] = []

        # 1. HIGH_AMOUNT (Weight: 0.20)
        # Transactions with unusually high amount (e.g. >= 200,000.0)
        r_high_amt = self.rules_by_key.get("HIGH_AMOUNT", {})
        if r_high_amt.get("enabled", True) and amount >= 200000.0:
            severity: RiskLevel = "CRITICAL" if amount >= 500000.0 else "HIGH"
            triggered.append(
                TriggeredRule(
                    rule_key="HIGH_AMOUNT",
                    description=r_high_amt["description"],
                    severity=severity,
                    weight=float(r_high_amt["weight"]),
                    field="amount",
                    value=f"${amount:,.2f}",
                )
            )

        # 2. ORIGIN_BALANCE_INCONSISTENCY (Weight: 0.20)
        # Mismatch between origin starting balance, debit, and ending balance
        r_orig_incon = self.rules_by_key.get("ORIGIN_BALANCE_INCONSISTENCY", {})
        balance_error_origin = old_org - amount - new_org
        if r_orig_incon.get("enabled", True) and abs(balance_error_origin) > 0.01:
            triggered.append(
                TriggeredRule(
                    rule_key="ORIGIN_BALANCE_INCONSISTENCY",
                    description=r_orig_incon["description"],
                    severity="HIGH",
                    weight=float(r_orig_incon["weight"]),
                    field="origin_balance_after",
                    value=f"Error delta: ${balance_error_origin:,.2f}",
                )
            )

        # 3. DESTINATION_BALANCE_INCONSISTENCY (Weight: 0.15)
        # Destination balance change not reflecting incoming credit
        r_dest_incon = self.rules_by_key.get("DESTINATION_BALANCE_INCONSISTENCY", {})
        balance_error_dest = old_dest + amount - new_dest
        if r_dest_incon.get("enabled", True) and abs(balance_error_dest) > 0.01:
            triggered.append(
                TriggeredRule(
                    rule_key="DESTINATION_BALANCE_INCONSISTENCY",
                    description=r_dest_incon["description"],
                    severity="MEDIUM",
                    weight=float(r_dest_incon["weight"]),
                    field="destination_balance_after",
                    value=f"Error delta: ${balance_error_dest:,.2f}",
                )
            )

        # 4. LARGE_BALANCE_CHANGE (Weight: 0.15)
        # Transaction depleting >= 80% of origin balance
        r_large_change = self.rules_by_key.get("LARGE_BALANCE_CHANGE", {})
        if r_large_change.get("enabled", True):
            is_large = False
            if old_org > 0 and (amount >= 0.80 * old_org or new_org == 0.0):
                is_large = True
            if is_large:
                ratio = (amount / old_org) if old_org > 0 else 1.0
                triggered.append(
                    TriggeredRule(
                        rule_key="LARGE_BALANCE_CHANGE",
                        description=r_large_change["description"],
                        severity="HIGH" if ratio >= 0.95 else "MEDIUM",
                        weight=float(r_large_change["weight"]),
                        field="origin_balance_before",
                        value=f"{min(100.0, ratio * 100):.1f}% of balance moved",
                    )
                )

        # 5. HIGH_RISK_TRANSACTION_TYPE (Weight: 0.15)
        # Transaction type is CASH_OUT or TRANSFER
        r_high_risk_type = self.rules_by_key.get("HIGH_RISK_TRANSACTION_TYPE", {})
        if r_high_risk_type.get("enabled", True) and tx_type_upper in ("CASH_OUT", "TRANSFER"):
            triggered.append(
                TriggeredRule(
                    rule_key="HIGH_RISK_TRANSACTION_TYPE",
                    description=r_high_risk_type["description"],
                    severity="MEDIUM",
                    weight=float(r_high_risk_type["weight"]),
                    field="type",
                    value=tx_type_upper,
                )
            )

        # 6. ZERO_BALANCE_ANOMALY (Weight: 0.10)
        # Transaction leaves zero balance on origin or destination
        r_zero_bal = self.rules_by_key.get("ZERO_BALANCE_ANOMALY", {})
        if r_zero_bal.get("enabled", True):
            is_zero_anomaly = (new_org == 0.0 and old_org > 0.0) or (new_dest == 0.0 and amount > 0.0)
            if is_zero_anomaly:
                triggered.append(
                    TriggeredRule(
                        rule_key="ZERO_BALANCE_ANOMALY",
                        description=r_zero_bal["description"],
                        severity="LOW",
                        weight=float(r_zero_bal["weight"]),
                        field="origin_balance_after" if new_org == 0.0 else "destination_balance_after",
                        value="Balance depleted to 0.00",
                    )
                )

        # Sum of weights
        raw_rule_score = sum(r.weight for r in triggered)
        raw_rule_score = max(0.0, min(1.0, float(raw_rule_score)))

        return triggered, raw_rule_score
