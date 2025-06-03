from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class ProductType(str, Enum):
    WORLD = "world"
    DLS = "dls"
    ACCOUNT = "account"
    GEMS = "gems"
    ITEMS = "items"
    OTHER = "other"

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"
    OUT_OF_STOCK = "out_of_stock"

class ProductBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50, description="Unique product code")
    name: str = Field(..., min_length=3, max_length=100, description="Product name")
    price: int = Field(..., gt=0, description="Price in World Locks")
    type: ProductType = Field(default=ProductType.WORLD)
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('code')
    def validate_code(cls, v):
        if not v.isalnum() and '_' not in v:
            raise ValueError("Code must be alphanumeric or contain underscore only")
        return v.upper()
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

class ProductFilter(BaseModel):
    name: Optional[str] = Field(None, description="Nama produk (bisa untuk pencarian partial)")
    category: Optional[str] = Field(None, description="Kategori produk")
    min_price: Optional[float] = Field(None, description="Harga minimum")
    max_price: Optional[float] = Field(None, description="Harga maksimum")
    available: Optional[bool] = Field(None, description="Filter hanya produk yang tersedia")
    start_date: Optional[datetime] = Field(None, description="Tanggal awal produk ditambahkan")
    end_date: Optional[datetime] = Field(None, description="Tanggal akhir produk ditambahkan")
    sort_by: Optional[str] = Field(None, description="Urutkan berdasarkan field tertentu (misal: price, name)")
    order: Optional[str] = Field(None, description="asc atau desc")

    class Config:
        schema_extra = {
            "example": {
                "name": "kopi",
                "category": "minuman",
                "min_price": 5000,
                "max_price": 30000,
                "available": True,
                "start_date": "2025-05-01T00:00:00",
                "end_date": "2025-06-01T23:59:59",
                "sort_by": "price",
                "order": "asc"
            }
        }

class ProductCreate(ProductBase):
    metadata: Optional[Dict] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "FARM_WORLD",
                "name": "Farm World Ready",
                "price": 100,
                "type": "world",
                "description": "Ready to harvest farm world with magplant",
                "metadata": {
                    "world_size": "100x60",
                    "has_magplant": True
                }
            }
        }

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    price: Optional[int] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=500)
    type: Optional[ProductType] = None
    status: Optional[ProductStatus] = None
    metadata: Optional[Dict] = None

class ProductResponse(ProductBase):
    id: Optional[int] = None
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)
    stock_count: int = Field(0, ge=0, description="Available stock count")
    total_stock: int = Field(0, ge=0, description="Total stock count")
    created_at: datetime = Field(
        default_factory=lambda: datetime.strptime("2025-05-28 14:57:46", "%Y-%m-%d %H:%M:%S")
    )
    updated_at: Optional[datetime] = None
    metadata: Dict = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "code": "FARM_WORLD",
                "name": "Farm World Ready",
                "price": 100,
                "type": "world",
                "description": "Ready to harvest farm world with magplant",
                "status": "active",
                "stock_count": 5,
                "total_stock": 10,
                "created_at": "2025-05-28 14:57:46",
                "metadata": {
                    "world_size": "100x60",
                    "has_magplant": True
                }
            }
        }