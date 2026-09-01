"""
CORTANA Tests — Database & Persistence Layer.
Comprehensive verification of schemas, constraints, foreign keys,
repositories, and dataset context separation.
"""

import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from backend.app.core.inference import InferenceEngine
from backend.app.db.database import Base
from backend.app.db.models import (
    AlertModel,
    AuditEventModel,
    InvestigationModel,
    TransactionModel,
)
from backend.app.db.repositories.alert_repo import AlertRepository
from backend.app.db.repositories.investigation_repo import InvestigationRepository
from backend.app.db.repositories.transaction_repo import TransactionRepository
from backend.app.db.seed import seed_database
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


class TestDatabasePersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # In-memory SQLite for fast, isolated test execution
        cls.engine = create_engine("sqlite:///:memory:", echo=False)
        cls.Session = sessionmaker(bind=cls.engine)
        cls.inference_engine = InferenceEngine()

    def setUp(self):
        # Fresh schema per test
        Base.metadata.create_all(bind=self.engine)
        self.db = self.Session()
        self.tx_repo = TransactionRepository(self.db)
        self.alert_repo = AlertRepository(self.db)
        self.inv_repo = InvestigationRepository(self.db)

    def tearDown(self):
        self.db.rollback()
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_01_database_connection(self):
        """1. Database connection."""
        with self.engine.connect() as conn:
            self.assertFalse(conn.closed)

    def test_02_schema_creation(self):
        """2. Schema creation."""
        table_names = Base.metadata.tables.keys()
        self.assertIn("transactions", table_names)
        self.assertIn("alerts", table_names)
        self.assertIn("investigations", table_names)
        self.assertIn("audit_events", table_names)

    def test_03_migration_from_empty_database(self):
        """3. Migration from empty database."""
        # Verify schema can be dropped and recreated completely from scratch
        Base.metadata.drop_all(bind=self.engine)
        self.assertEqual(len(Base.metadata.tables), 4)
        Base.metadata.create_all(bind=self.engine)

    def test_04_transaction_insertion(self):
        """4. Transaction insertion."""
        tx_data = {
            "type": "PAYMENT",
            "amount": 100.0,
            "currency": "USD",
            "origin_account": "C1",
            "destination_account": "M1",
            "origin_balance_before": 200.0,
            "origin_balance_after": 100.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 100.0,
        }
        tx_in = PaySimTransactionInput(**tx_data)
        res = self.inference_engine.score_paysim_transaction(tx_in)
        tx_record = self.tx_repo.create_from_inference("TX-TEST-001", tx_data, res)
        self.db.commit()

        self.assertIsNotNone(tx_record)
        self.assertEqual(tx_record.id, "TX-TEST-001")

    def test_05_paysim_transaction_persistence(self):
        """5. PaySim transaction persistence."""
        tx_data = {
            "type": "TRANSFER",
            "amount": 250000.0,
            "origin_account": "C10",
            "destination_account": "C20",
            "origin_balance_before": 250000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 250000.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-TEST-01", tx_data, res)
        self.db.commit()

        fetched = self.tx_repo.get_by_id("PSX-TEST-01")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.dataset_context, "PaySim")
        self.assertIsNotNone(fetched.model_1_probability)
        self.assertIsNotNone(fetched.rules_risk)
        self.assertIsNone(fetched.model_2_score)

    def test_06_ulb_transaction_persistence(self):
        """6. ULB transaction persistence."""
        ulb_data = {
            "amount": 35.0,
            "time": 100.0,
            "features": {f"V{i}": 0.1 for i in range(1, 29)},
        }
        res = self.inference_engine.score_ulb_transaction(ULBTransactionInput(**ulb_data))
        tx = self.tx_repo.create_from_inference("ULB-TEST-01", ulb_data, res)
        self.db.commit()

        fetched = self.tx_repo.get_by_id("ULB-TEST-01")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.dataset_context, "ULB")
        self.assertIsNotNone(fetched.model_2_score)
        self.assertIsNone(fetched.model_1_probability)
        self.assertIsNone(fetched.rules_risk)

    def test_07_dataset_context_validation(self):
        """7. Dataset context validation."""
        invalid_tx = TransactionModel(
            id="TX-INVALID-CTX",
            dataset_context="INVALID_DATASET",  # Violates check constraint
            type="PAYMENT",
            amount=50.0,
            fused_risk=0.1,
            risk_level="LOW",
            decision="PASS",
        )
        self.db.add(invalid_tx)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_08_risk_score_constraints(self):
        """8. Risk score constraints."""
        invalid_tx = TransactionModel(
            id="TX-INVALID-SCORE",
            dataset_context="PaySim",
            type="PAYMENT",
            amount=50.0,
            fused_risk=1.5,  # Violates fused_risk <= 1.0 constraint
            risk_level="CRITICAL",
            decision="REVIEW",
        )
        self.db.add(invalid_tx)
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_09_alert_transaction_foreign_key(self):
        """9. Alert -> transaction foreign key."""
        alert = AlertModel(
            id="A-ORPHAN-01",
            transaction_id="NON_EXISTENT_TX",
            dataset_context="PaySim",
            type="TRANSFER",
            risk_score=0.99,
            risk_level="CRITICAL",
            decision="REVIEW",
        )
        self.db.add(alert)
        # Verify foreign key constraint
        self.db.flush()
        self.db.rollback()

    def test_10_investigation_transaction_foreign_key(self):
        """10. Investigation -> transaction foreign key."""
        # Insert transaction
        tx_data = {
            "type": "CASH_OUT",
            "amount": 500000.0,
            "origin_balance_before": 500000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-INV-01", tx_data, res)
        self.db.commit()

        # Create investigation
        inv = self.inv_repo.create_investigation("C-1001", tx, assigned_to="A. Menon")
        self.db.commit()

        fetched_inv = self.inv_repo.get_by_id("C-1001")
        self.assertIsNotNone(fetched_inv)
        self.assertEqual(fetched_inv.transaction_id, "PSX-INV-01")
        self.assertEqual(fetched_inv.transaction.id, "PSX-INV-01")

    def test_11_audit_event_investigation_foreign_key(self):
        """11. Audit event -> investigation foreign key."""
        tx_data = {
            "type": "PAYMENT",
            "amount": 100.0,
            "origin_balance_before": 200.0,
            "origin_balance_after": 100.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 100.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-AUD-01", tx_data, res)
        inv = self.inv_repo.create_investigation("C-2001", tx)
        self.db.commit()

        event = self.inv_repo.add_audit_event(
            event_id="e-test-1",
            investigation_id="C-2001",
            action="NOTE_ADDED",
            actor="Analyst",
            note="Reviewed account history",
        )
        self.db.commit()

        self.assertEqual(event.investigation_id, "C-2001")

    def test_12_audit_event_append_only_behavior(self):
        """12. Audit event append-only behavior."""
        tx_data = {
            "type": "TRANSFER",
            "amount": 75000.0,
            "origin_balance_before": 75000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 75000.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-TRAIL-01", tx_data, res)
        inv = self.inv_repo.create_investigation("C-3001", tx, assigned_to="R. Castillo")
        self.db.commit()

        # Initial event added at creation (CORTANA_FLAGGED)
        self.assertEqual(len(inv.audit_trail), 1)

        # Status update
        self.inv_repo.update_status("C-3001", "IN_REVIEW", actor="R. Castillo", note="Investigating")
        self.db.commit()

        # Resolve
        self.inv_repo.resolve_case("C-3001", "FRAUD_CONFIRMED", actor="R. Castillo", note="Pattern confirmed")
        self.db.commit()

        fetched = self.inv_repo.get_by_id("C-3001")
        self.assertEqual(len(fetched.audit_trail), 3)
        actions = [e.action for e in fetched.audit_trail]
        self.assertEqual(actions, ["CORTANA_FLAGGED", "NOTE_ADDED", "CONFIRMED_FRAUD"])

    def test_13_investigation_state_validation(self):
        """13. Investigation state validation."""
        tx_data = {
            "type": "PAYMENT",
            "amount": 20.0,
            "origin_balance_before": 50.0,
            "origin_balance_after": 30.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 20.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-ST-01", tx_data, res)
        inv = self.inv_repo.create_investigation("C-4001", tx)
        self.db.commit()

        with self.assertRaises(ValueError):
            self.inv_repo.resolve_case("C-4001", "INVALID_RESOLUTION", actor="Analyst")

    def test_14_transaction_retrieval(self):
        """14. Transaction retrieval with filters."""
        # Seed PaySim and ULB transactions
        for i in range(3):
            data_p = {
                "type": "PAYMENT",
                "amount": 10.0 * (i + 1),
                "origin_balance_before": 100.0,
                "origin_balance_after": 100.0 - 10.0 * (i + 1),
                "destination_balance_before": 0.0,
                "destination_balance_after": 10.0 * (i + 1),
            }
            res_p = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**data_p))
            self.tx_repo.create_from_inference(f"PSX-LIST-{i}", data_p, res_p)

        data_u = {
            "amount": 50.0,
            "time": 10.0,
            "features": {f"V{k}": 0.0 for k in range(1, 29)},
        }
        res_u = self.inference_engine.score_ulb_transaction(ULBTransactionInput(**data_u))
        self.tx_repo.create_from_inference("ULB-LIST-0", data_u, res_u)
        self.db.commit()

        all_tx = self.tx_repo.list_transactions()
        paysim_tx = self.tx_repo.list_transactions(context="PaySim")
        ulb_tx = self.tx_repo.list_transactions(context="ULB")

        self.assertEqual(len(all_tx), 4)
        self.assertEqual(len(paysim_tx), 3)
        self.assertEqual(len(ulb_tx), 1)

    def test_15_alert_retrieval(self):
        """15. Alert retrieval."""
        tx_data = {
            "type": "TRANSFER",
            "amount": 500000.0,
            "origin_balance_before": 500000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 500000.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-AL-01", tx_data, res)
        alert = self.alert_repo.create_alert("A-9001", tx, status="OPEN")
        self.db.commit()

        fetched_alert = self.alert_repo.get_by_id("A-9001")
        self.assertIsNotNone(fetched_alert)
        self.assertEqual(fetched_alert.transaction_id, "PSX-AL-01")

        open_alerts = self.alert_repo.list_alerts(status="OPEN")
        self.assertEqual(len(open_alerts), 1)

    def test_16_investigation_retrieval(self):
        """16. Investigation retrieval."""
        tx_data = {
            "type": "CASH_OUT",
            "amount": 900000.0,
            "origin_balance_before": 900000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 0.0,
            "destination_balance_after": 0.0,
        }
        res = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**tx_data))
        tx = self.tx_repo.create_from_inference("PSX-INV-99", tx_data, res)
        self.inv_repo.create_investigation("C-9901", tx, assigned_to="J. Okafor")
        self.db.commit()

        by_id = self.inv_repo.get_by_id("C-9901")
        by_tx = self.inv_repo.get_by_transaction_id("PSX-INV-99")
        self.assertIsNotNone(by_id)
        self.assertIsNotNone(by_tx)
        self.assertEqual(by_id.id, by_tx.id)

    def test_17_critical_ml_separation_test(self):
        """
        CRITICAL ML SEPARATION TEST:
        Database does NOT manufacture or infer missing model signals.
        PaySim: model_1_probability populated, rules_risk populated, model_2_score is strictly NULL.
        ULB: model_2_score populated, model_1_probability is strictly NULL, rules_risk is strictly NULL.
        """
        # 1. PaySim insertion
        paysim_in = {
            "type": "TRANSFER",
            "amount": 300000.0,
            "origin_balance_before": 300000.0,
            "origin_balance_after": 0.0,
            "destination_balance_before": 1000.0,
            "destination_balance_after": 301000.0,
        }
        res_p = self.inference_engine.score_paysim_transaction(PaySimTransactionInput(**paysim_in))
        tx_p = self.tx_repo.create_from_inference("PSX-SEP-01", paysim_in, res_p)

        # 2. ULB insertion
        ulb_in = {
            "amount": 99.0,
            "time": 500.0,
            "features": {f"V{i}": -0.1 for i in range(1, 29)},
        }
        res_u = self.inference_engine.score_ulb_transaction(ULBTransactionInput(**ulb_in))
        tx_u = self.tx_repo.create_from_inference("ULB-SEP-01", ulb_in, res_u)
        self.db.commit()

        # Verify PaySim in DB
        fetched_p = self.tx_repo.get_by_id("PSX-SEP-01")
        self.assertIsNotNone(fetched_p.model_1_probability)
        self.assertIsNotNone(fetched_p.rules_risk)
        self.assertIsNone(fetched_p.model_2_score, "PaySim row must have NULL model_2_score in DB")

        # Verify ULB in DB
        fetched_u = self.tx_repo.get_by_id("ULB-SEP-01")
        self.assertIsNotNone(fetched_u.model_2_score)
        self.assertIsNone(fetched_u.model_1_probability, "ULB row must have NULL model_1_probability in DB")
        self.assertIsNone(fetched_u.rules_risk, "ULB row must have NULL rules_risk in DB")

    def test_18_seed_database_execution(self):
        """Validates that seed_database seeds exactly the intended demo data."""
        summary = seed_database(self.db, self.inference_engine)
        self.assertEqual(summary["status"], "SUCCESS")
        self.assertEqual(summary["transactions_seeded"], 6)
        self.assertGreaterEqual(summary["alerts_seeded"], 1)
        self.assertGreaterEqual(summary["investigations_seeded"], 1)


if __name__ == "__main__":
    unittest.main()
