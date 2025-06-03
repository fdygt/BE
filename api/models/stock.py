from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from .balance import CurrencyType  # Import CurrencyType

class StockStatus(str, Enum):
    AVAILABLE = "available"
    SOLD = "sold"
    RESERVED = "reserved"
    EXPIRED = "expired"
    INVALID = "invalid"

class PriceInfo(BaseModel):
    wl_price: Optional[int] = Field(0, ge=0)
    dl_price: Optional[int] = Field(0, ge=0)
    bgl_price: Optional[int] = Field(0, ge=0)
    rupiah_price: int = Field(..., ge=0)  # Wajib ada harga Rupiah

    @validator('*')
    def validate_non_negative(cls, v):
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v

class StockItem(BaseModel):
    id: Optional[int] = None
    product_code: str = Field(..., description="Product code this stock belongs to")
    content: str = Field(..., min_length=1, description="Stock content (world name, account details, etc)")
    prices: PriceInfo
    status: StockStatus = Field(default=StockStatus.AVAILABLE)
    available_for: List[str] = Field(
        default=["discord", "web"],
        description="User types that can purchase this item"
    )
    added_by: str = Field(default="fdygt")
    added_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:06:08",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    updated_at: Optional[datetime] = None
    buyer_id: Optional[str] = None
    seller_id: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

    @validator('available_for')
    def validate_available_for(cls, v):
        valid_types = ["discord", "web"]
        if not all(t in valid_types for t in v):
            raise ValueError(f"Invalid user type. Must be one of: {valid_types}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "product_code": "FARM_WORLD",
                "content": "FARMWORLD1",
                "prices": {
                    "wl_price": 100,
                    "dl_price": 1,
                    "bgl_price": 0,
                    "rupiah_price": 50000
                },
                "status": "available",
                "available_for": ["discord", "web"],
                "added_by": "fdygt",
                "added_at": "2025-06-02 13:06:08",
                "metadata": {
                    "world_type": "farm",
                    "has_magplant": True
                }
            }
        }

class StockResponse(BaseModel):
    stock_id: str = Field(..., description="ID unik saham/stok")
    name: str = Field(..., description="Nama saham/stok")
    symbol: str = Field(..., description="Kode atau simbol saham")
    price: float = Field(..., description="Harga saat ini")
    quantity: int = Field(..., description="Jumlah tersedia/dimiliki")
    currency: str = Field("IDR", description="Kode mata uang")
    last_update: Optional[datetime] = Field(None, description="Waktu update terakhir")
    description: Optional[str] = Field(None, description="Keterangan tambahan")
    
    class Config:
        schema_extra = {
            "example": {
                "stock_id": "STK001",
                "name": "PT. ABC Tbk",
                "symbol": "ABC",
                "price": 3300.0,
                "quantity": 50,
                "currency": "IDR",
                "last_update": "2025-06-02T16:57:06",
                "description": "Saham teknologi unggulan"
            }
        }

class StockAddRequest(BaseModel):
    product_code: str = Field(..., description="Product code to add stock to")
    items: List[str] = Field(..., min_items=1, description="List of stock contents to add")
    prices: PriceInfo
    available_for: List[str] = Field(
        default=["discord", "web"],
        description="User types that can purchase this item"
    )
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    @validator('items')
    def validate_items(cls, v):
        if not all(item.strip() for item in v):
            raise ValueError("Stock items cannot be empty")
        return [item.strip() for item in v]

    @validator('available_for')
    def validate_available_for(cls, v):
        valid_types = ["discord", "web"]
        if not all(t in valid_types for t in v):
            raise ValueError(f"Invalid user type. Must be one of: {valid_types}")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "product_code": "FARM_WORLD",
                "items": ["FARMWORLD1", "FARMWORLD2"],
                "prices": {
                    "wl_price": 100,
                    "dl_price": 1,
                    "bgl_price": 0,
                    "rupiah_price": 50000
                },
                "available_for": ["discord", "web"],
                "metadata": {
                    "world_type": "farm",
                    "has_magplant": True
                }
            }
        }

class StockReduceRequest(BaseModel):
    item_ids: List[int] = Field(..., min_items=1, description="List of stock IDs to reduce")
    reason: str = Field(..., description="Reason for stock reduction")
    buyer_id: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "item_ids": [1, 2, 3],
                "reason": "Sold to user",
                "buyer_id": "usr_12345"
            }
        }

class StockHistoryType(str, Enum):
    ADD = "add"
    REDUCE = "reduce"
    UPDATE = "update"
    RESERVE = "reserve"
    CANCEL = "cancel"
    EXPIRE = "expire"
    INVALID = "invalid"

class StockHistoryResponse(BaseModel):
    id: int
    stock_id: int
    type: StockHistoryType
    product_code: str
    content: str
    previous_status: Optional[StockStatus]
    new_status: StockStatus
    prices: PriceInfo
    action_by: str
    action_at: datetime = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:06:08",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    buyer_id: Optional[str]
    seller_id: Optional[str]
    reason: Optional[str]
    metadata: Dict = Field(default_factory=dict)


class StockFilter(BaseModel):
    product_code: Optional[str] = None
    status: Optional[StockStatus] = None
    min_price: Optional[Dict[str, int]] = Field(
        default_factory=lambda: {
            "wl_price": 0,
            "dl_price": 0,
            "bgl_price": 0,
            "rupiah_price": 0
        }
    )
    max_price: Optional[Dict[str, int]] = None
    available_for: Optional[List[str]] = None
    added_by: Optional[str] = None
    buyer_id: Optional[str] = None
    seller_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = Field(
        default_factory=lambda: datetime.strptime(
            "2025-06-02 13:12:49",
            "%Y-%m-%d %H:%M:%S"
        )
    )
    metadata_filters: Optional[Dict] = Field(default_factory=dict)

    @validator('available_for')
    def validate_available_for(cls, v):
        if v is not None:
            valid_types = ["discord", "web"]
            if not all(t in valid_types for t in v):
                raise ValueError(f"Invalid user type. Must be one of: {valid_types}")
        return v

    @validator('min_price', 'max_price')
    def validate_prices(cls, v):
        if v is not None:
            valid_currencies = ["wl_price", "dl_price", "bgl_price", "rupiah_price"]
            for key in v.keys():
                if key not in valid_currencies:
                    raise ValueError(f"Invalid currency type. Must be one of: {valid_currencies}")
            for value in v.values():
                if value < 0:
                    raise ValueError("Price cannot be negative")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "product_code": "FARM_WORLD",
                "status": "available",
                "min_price": {
                    "wl_price": 50,
                    "dl_price": 0,
                    "bgl_price": 0,
                    "rupiah_price": 25000
                },
                "max_price": {
                    "wl_price": 200,
                    "dl_price": 2,
                    "bgl_price": 0,
                    "rupiah_price": 100000
                },
                "available_for": ["discord", "web"],
                "added_by": "fdygt",
                "start_date": "2025-06-01 00:00:00",
                "end_date": "2025-06-02 13:12:49",
                "metadata_filters": {
                    "world_type": "farm",
                    "has_magplant": True
                }
            }
        }

# Log creation
import logging
logger = logging.getLogger(__name__)
logger.info(f"""
Stock models initialized:
Time: 2025-06-02 13:12:49
User: fdygt
""")