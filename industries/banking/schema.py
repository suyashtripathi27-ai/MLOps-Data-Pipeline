"""
Banking input schema models.

Uses Pydantic when available, with a lightweight fallback to keep runtime safe
in environments where pydantic is not installed.
"""

from typing import Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - fallback path
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default=None, **kwargs):
        return default


class BankingTransactionSchema(BaseModel):
    """Expected banking transaction fields."""

    transaction_id: Optional[str] = Field(default=None)
    account_id: Optional[str] = Field(default=None)
    transaction_date: Optional[str] = Field(default=None)
    transaction_type: Optional[str] = Field(default=None)
    amount: Optional[float] = Field(default=None)
    balance: Optional[float] = Field(default=None)
    branch_id: Optional[str] = Field(default=None)
    product_type: Optional[str] = Field(default=None)
    customer_id: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default=None)
    interest_earned: Optional[float] = Field(default=None)
    fees_charged: Optional[float] = Field(default=None)
