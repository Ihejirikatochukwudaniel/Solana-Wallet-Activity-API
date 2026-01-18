"""
Pydantic models for API request/response validation.
Includes validators for Solana addresses and transaction data.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class WalletSummary(BaseModel):
    """Response model for wallet summary endpoint."""

    address: str = Field(..., description="Solana wallet address")
    balance: float = Field(..., description="Balance in SOL")
    balance_lamports: int = Field(..., description="Balance in lamports")
    tx_count: int = Field(..., description="Total transaction count")
    last_active: Optional[datetime] = Field(
        None, description="Timestamp of last transaction"
    )

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Solana address format (base58, 32-44 characters)."""
        if not v:
            raise ValueError("Address cannot be empty")
        if len(v) < 32 or len(v) > 44:
            raise ValueError(
                f"Invalid Solana address length: {len(v)}. Expected 32-44 characters"
            )
        # Basic base58 validation (only alphanumeric, no 0, O, I, l)
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if not all(c in base58_chars for c in v):
            raise ValueError("Invalid Solana address: contains non-base58 characters")
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "balance": 1.42,
                "balance_lamports": 1420000000,
                "tx_count": 37,
                "last_active": "2026-01-15T10:22:00Z",
            }
        }


class Transaction(BaseModel):
    """Model for individual transaction data."""

    signature: str = Field(..., description="Transaction signature")
    block_time: datetime = Field(..., description="Block time (UTC)")
    slot: int = Field(..., description="Slot number")
    status: str = Field(..., description="Transaction status (success/failed)")
    fee: int = Field(..., description="Transaction fee in lamports")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "signature": "5wJ8nk9V5vZ2K6y3P4q5R6s7T8u9V0w1X2y3Z4a5B6c7D8e9F0g1H2i3J4k5L",
                "block_time": "2026-01-16T10:22:00Z",
                "slot": 123456789,
                "status": "success",
                "fee": 5000,
            }
        }


class TransactionList(BaseModel):
    """Response model for transactions endpoint."""

    address: str = Field(..., description="Solana wallet address")
    transactions: List[Transaction] = Field(..., description="List of transactions")
    count: int = Field(..., description="Number of transactions in response")

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate Solana address format (base58, 32-44 characters)."""
        if not v:
            raise ValueError("Address cannot be empty")
        if len(v) < 32 or len(v) > 44:
            raise ValueError(
                f"Invalid Solana address length: {len(v)}. Expected 32-44 characters"
            )
        base58_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        if not all(c in base58_chars for c in v):
            raise ValueError("Invalid Solana address: contains non-base58 characters")
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
                "transactions": [
                    {
                        "signature": "5wJ8nk9V5vZ2K6y3P4q5R6s7T8u9V0w1X2y3Z4a5B6c7D8e9F0g1H2i3J4k5L",
                        "block_time": "2026-01-16T10:22:00Z",
                        "slot": 123456789,
                        "status": "success",
                        "fee": 5000,
                    }
                ],
                "count": 1,
            }
        }
