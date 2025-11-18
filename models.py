from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserContext(BaseModel):
    userId: str
    userTier: str
    country: str
    lifetimeSpend: float
    ordersPlaced: int


class CartItem(BaseModel):
    productId: str
    category: str
    unitPrice: float
    quantity: int


class Cart(BaseModel):
    items: List[CartItem]


class Eligibility(BaseModel):
    allowedUserTiers: List[str] = None
    minLifetimeSpend: float = None
    minOrdersPlaced: int = None
    firstOrderOnly: bool = None
    allowedCountries: List[str] = None
    minCartValue: float = None
    applicableCategories: List[str] = None
    excludedCategories: List[str] = None
    minItemsCount: int = None


class Coupon(BaseModel):
    code: str
    description: str
    discountType: str
    discountValue: float
    maxDiscountAmount: float = None
    startDate: datetime
    endDate: datetime
    usageLimitPerUser: int = None
    eligibility: Eligibility


class BestCouponRequest(BaseModel):
    user: UserContext
    cart: Cart


class LoginRequest(BaseModel):
    email: str
    password: str
