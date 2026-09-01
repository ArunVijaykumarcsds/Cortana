"""
CORTANA — Transaction Input Schemas.
Data contracts for incoming PaySim and ULB transactions.
"""

from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


TransactionType = Literal["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"]
DatasetContext = Literal["PaySim", "ULB"]


class PaySimTransactionInput(BaseModel):
    """
    Input schema for PaySim transactions.
    Evaluated by Model 1 (Random Forest) and the Behavioral Rules Engine.
    """
    id: Optional[str] = Field(default=None, description="Unique transaction ID (e.g., PSX-100001)")
    dataset_context: Literal["PaySim"] = Field(default="PaySim", description="Must be 'PaySim'")
    type: TransactionType = Field(..., description="Transaction type")
    amount: float = Field(..., ge=0.0, description="Transaction monetary amount")
    origin_account: Optional[str] = Field(default="", description="Origin account identifier")
    destination_account: Optional[str] = Field(default="", description="Destination account identifier")
    origin_balance_before: float = Field(..., ge=0.0, description="Origin account balance before transaction")
    origin_balance_after: float = Field(..., ge=0.0, description="Origin account balance after transaction")
    destination_balance_before: float = Field(..., ge=0.0, description="Destination account balance before transaction")
    destination_balance_after: float = Field(..., ge=0.0, description="Destination account balance after transaction")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp")


class ULBTransactionInput(BaseModel):
    """
    Input schema for ULB Credit Card Fraud transactions.
    Evaluated strictly by Model 2 (Isolation Forest).
    Requires the 30 continuous PCA features: Time, V1-V28, and Amount.
    """
    id: Optional[str] = Field(default=None, description="Unique transaction ID (e.g., ULB-200001)")
    dataset_context: Literal["ULB"] = Field(default="ULB", description="Must be 'ULB'")
    amount: float = Field(..., ge=0.0, description="Transaction monetary amount")
    currency: Optional[str] = Field(default="USD", description="Currency code")
    origin_account: Optional[str] = Field(default="", description="Card / Account identifier")
    destination_account: Optional[str] = Field(default="", description="Merchant identifier")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp")
    
    # 30 ULB continuous features
    time: float = Field(default=0.0, description="Seconds elapsed since first transaction")
    features: Dict[str, float] = Field(
        ...,
        description="Dictionary mapping V1 through V28 (and optionally Time, Amount) to numeric floats."
    )


TransactionInput = Union[PaySimTransactionInput, ULBTransactionInput]
