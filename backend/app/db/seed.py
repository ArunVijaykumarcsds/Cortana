"""
CORTANA — Development / Demo Database Seeder.
Generates a small deterministic set of scored transactions, alerts,
and investigations for local development and testing.

DOES NOT modify or replace any validated evaluation datasets.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from backend.app.core.inference import InferenceEngine
from backend.app.db.database import get_db_context
from backend.app.db.repositories.alert_repo import AlertRepository
from backend.app.db.repositories.investigation_repo import InvestigationRepository
from backend.app.db.repositories.transaction_repo import TransactionRepository
from backend.app.schemas.transaction import PaySimTransactionInput, ULBTransactionInput


DEMO_PAYSIM_TRANSACTIONS = [
    {
        "id": "PSX-100001",
        "dataset_context": "PaySim",
        "type": "PAYMENT",
        "amount": 125.50,
        "currency": "USD",
        "origin_account": "C10001",
        "destination_account": "M90001",
        "origin_balance_before": 1500.00,
        "origin_balance_after": 1374.50,
        "destination_balance_before": 0.00,
        "destination_balance_after": 125.50,
        "mins_ago": 180,
    },
    {
        "id": "PSX-100002",
        "dataset_context": "PaySim",
        "type": "TRANSFER",
        "amount": 250000.00,
        "currency": "USD",
        "origin_account": "C10002",
        "destination_account": "C90002",
        "origin_balance_before": 250000.00,
        "origin_balance_after": 0.00,
        "destination_balance_before": 1000.00,
        "destination_balance_after": 251000.00,
        "mins_ago": 120,
    },
    {
        "id": "PSX-100003",
        "dataset_context": "PaySim",
        "type": "CASH_OUT",
        "amount": 650000.00,
        "currency": "USD",
        "origin_account": "C10003",
        "destination_account": "M90003",
        "origin_balance_before": 650000.00,
        "origin_balance_after": 0.00,
        "destination_balance_before": 0.00,
        "destination_balance_after": 0.00,  # anomalous zero
        "mins_ago": 60,
    },
    {
        "id": "PSX-100004",
        "dataset_context": "PaySim",
        "type": "PAYMENT",
        "amount": 42.00,
        "currency": "USD",
        "origin_account": "C10004",
        "destination_account": "M90004",
        "origin_balance_before": 300.00,
        "origin_balance_after": 258.00,
        "destination_balance_before": 5000.00,
        "destination_balance_after": 5042.00,
        "mins_ago": 30,
    },
]

DEMO_ULB_TRANSACTIONS = [
    {
        "id": "ULB-200001",
        "dataset_context": "ULB",
        "amount": 149.62,
        "currency": "USD",
        "origin_account": "CC-4001",
        "destination_account": "MERCH-8001",
        "time": 406.0,
        "features": {f"V{i}": -0.05 for i in range(1, 29)},
        "mins_ago": 90,
    },
    {
        "id": "ULB-200002",
        "dataset_context": "ULB",
        "amount": 529.00,
        "currency": "USD",
        "origin_account": "CC-4002",
        "destination_account": "MERCH-8002",
        "time": 472.0,
        "features": {
            **{f"V{i}": 0.0 for i in range(1, 29)},
            "V1": -4.39,
            "V2": 3.65,
            "V3": -6.78,
            "V4": 5.21,
            "V5": -4.12,
        },
        "mins_ago": 15,
    },
]


def seed_database(db: Session, inference_engine: InferenceEngine) -> dict:
    """
    Deterministically seeds the database using the live inference engine.
    """
    tx_repo = TransactionRepository(db)
    alert_repo = AlertRepository(db)
    inv_repo = InvestigationRepository(db)

    now = datetime.now(timezone.utc)
    seeded_txs = []
    seeded_alerts = []
    seeded_invs = []

    # 1. Seed PaySim demo transactions
    for d in DEMO_PAYSIM_TRANSACTIONS:
        tx_input = PaySimTransactionInput(**d)
        res = inference_engine.score_paysim_transaction(tx_input)
        ts = now - timedelta(minutes=d["mins_ago"])
        tx_model = tx_repo.create_from_inference(
            tx_id=d["id"],
            input_data=d,
            inference_result=res,
            timestamp=ts,
        )
        seeded_txs.append(tx_model.id)

        # Trigger alert and investigation if high/critical or review
        if tx_model.risk_level in ("HIGH", "CRITICAL") or tx_model.decision == "REVIEW":
            alert_id = f"A-{len(seeded_alerts) + 5001}"
            alert = alert_repo.create_alert(alert_id=alert_id, transaction=tx_model, timestamp=ts)
            seeded_alerts.append(alert.id)

            if tx_model.decision == "REVIEW":
                case_id = f"C-{len(seeded_invs) + 10201}"
                inv = inv_repo.create_investigation(
                    case_id=case_id,
                    transaction=tx_model,
                    assigned_to="A. Menon",
                    opened_at=ts,
                )
                seeded_invs.append(inv.id)

    # 2. Seed ULB demo transactions
    for d in DEMO_ULB_TRANSACTIONS:
        tx_input = ULBTransactionInput(**d)
        res = inference_engine.score_ulb_transaction(tx_input)
        ts = now - timedelta(minutes=d["mins_ago"])
        tx_model = tx_repo.create_from_inference(
            tx_id=d["id"],
            input_data=d,
            inference_result=res,
            timestamp=ts,
        )
        seeded_txs.append(tx_model.id)

        if tx_model.risk_level in ("HIGH", "CRITICAL") or tx_model.decision == "REVIEW":
            alert_id = f"A-{len(seeded_alerts) + 5001}"
            alert = alert_repo.create_alert(alert_id=alert_id, transaction=tx_model, timestamp=ts)
            seeded_alerts.append(alert.id)

    db.commit()

    return {
        "status": "SUCCESS",
        "transactions_seeded": len(seeded_txs),
        "alerts_seeded": len(seeded_alerts),
        "investigations_seeded": len(seeded_invs),
    }


if __name__ == "__main__":
    engine = InferenceEngine()
    with get_db_context() as db:
        summary = seed_database(db, engine)
        print("Database seeding completed:", summary)
