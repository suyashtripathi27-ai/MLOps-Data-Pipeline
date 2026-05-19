"""
Retail input schema models.

Uses Pydantic when available, with a lightweight fallback to keep runtime safe
in environments where pydantic is not installed.
"""

from typing import Optional

try:
    from pydantic import BaseModel, Field
except Exception:  # pragma: no cover - fallback path for lightweight runtime
    class BaseModel:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default=None, **kwargs):
        return default


class RetailTransactionSchema(BaseModel):
    """Expected retail transaction fields."""

    transaction_id: Optional[str] = Field(default=None)
    date: Optional[str] = Field(default=None)
    store_id: Optional[str] = Field(default=None)
    department: Optional[str] = Field(default=None)
    customer_id: Optional[str] = Field(default=None)
    revenue: Optional[float] = Field(default=None)
    quantity_sold: Optional[float] = Field(default=None)
    inventory_level: Optional[float] = Field(default=None)
    discount_pct: Optional[float] = Field(default=None)
    is_holiday: Optional[bool] = Field(default=None)
    is_promo: Optional[bool] = Field(default=None)
    employee_count: Optional[float] = Field(default=None)
    labor_cost: Optional[float] = Field(default=None)


class RetailRequiredColumnsSchema(BaseModel):
    """Schema for validating required columns at ingestion."""

    revenue: str = Field(default="revenue")
    date: str = Field(default="date")
    store_id: str = Field(default="store_id")
