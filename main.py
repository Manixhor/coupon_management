from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from models import *

app = FastAPI()

# Storage
coupons = {}
users = {}
usage = {}

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "secret-key"
ALGORITHM = "HS256"


# Initialize demo user with PRE-HASHED password
# Password: HireMe@2025!
# This hash was generated separately to avoid re-hashing
users["hire-me@anshumat.org"] = {
    "email": "hire-me@anshumat.org",
    "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5yvSOwv2u/RMy"
}

# Initialize sample coupons
coupons["WELCOME100"] = Coupon(
    code="WELCOME100",
    description="Welcome offer",
    discountType="FLAT",
    discountValue=100,
    startDate=datetime(2025, 1, 1),
    endDate=datetime(2025, 12, 31),
    usageLimitPerUser=1,
    eligibility=Eligibility(
        allowedUserTiers=["NEW"],
        firstOrderOnly=True,
        minCartValue=500
    )
)


def get_cart_total(cart):
    total = 0
    for item in cart.items:
        total += item.unitPrice * item.quantity
    return total


def get_cart_categories(cart):
    categories = []
    for item in cart.items:
        if item.category not in categories:
            categories.append(item.category)
    return categories


def get_item_count(cart):
    count = 0
    for item in cart.items:
        count += item.quantity
    return count


def check_eligibility(coupon, user, cart):
    e = coupon.eligibility
    
    # Check date
    now = datetime.now()
    if not (coupon.startDate <= now <= coupon.endDate):
        return False
    
    # Check usage limit
    if coupon.usageLimitPerUser:
        used = usage.get(user.userId, {}).get(coupon.code, 0)
        if used >= coupon.usageLimitPerUser:
            return False
    
    # Check user tier
    if e.allowedUserTiers:
        if user.userTier not in e.allowedUserTiers:
            return False
    
    # Check lifetime spend
    if e.minLifetimeSpend:
        if user.lifetimeSpend < e.minLifetimeSpend:
            return False
    
    # Check orders placed
    if e.minOrdersPlaced:
        if user.ordersPlaced < e.minOrdersPlaced:
            return False
    
    # Check first order only
    if e.firstOrderOnly:
        if user.ordersPlaced != 0:
            return False
    
    # Check country
    if e.allowedCountries:
        if user.country not in e.allowedCountries:
            return False
    
    # Check cart value
    if e.minCartValue:
        if get_cart_total(cart) < e.minCartValue:
            return False
    
    # Check applicable categories
    if e.applicableCategories:
        cart_cats = get_cart_categories(cart)
        found = False
        for cat in cart_cats:
            if cat in e.applicableCategories:
                found = True
                break
        if not found:
            return False
    
    # Check excluded categories
    if e.excludedCategories:
        cart_cats = get_cart_categories(cart)
        for cat in cart_cats:
            if cat in e.excludedCategories:
                return False
    
    # Check min items
    if e.minItemsCount:
        if get_item_count(cart) < e.minItemsCount:
            return False
    
    return True


def calculate_discount(coupon, cart):
    cart_total = get_cart_total(cart)
    
    if coupon.discountType == "FLAT":
        discount = coupon.discountValue
        if discount > cart_total:
            discount = cart_total
        return discount
    
    if coupon.discountType == "PERCENT":
        discount = (coupon.discountValue / 100) * cart_total
        if coupon.maxDiscountAmount:
            if discount > coupon.maxDiscountAmount:
                discount = coupon.maxDiscountAmount
        if discount > cart_total:
            discount = cart_total
        return discount
    
    return 0


@app.get("/")
def home():
    return {
        "message": "Coupon System",
        "demo_login": {
            "email": "hire-me@anshumat.org",
            "password": "HireMe@2025!"
        }
    }


@app.post("/auth/login")
def login(request: LoginRequest):
    user = users.get(request.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not pwd_context.verify(request.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = jwt.encode(
        {"sub": request.email, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return {"access_token": token, "token_type": "bearer"}


@app.post("/coupons/")
def create_coupon(coupon: Coupon):
    coupons[coupon.code] = coupon
    return coupon


@app.get("/coupons/")
def get_coupons():
    return list(coupons.values())


@app.post("/coupons/best")
def get_best_coupon(request: BestCouponRequest):
    applicable = []
    
    for coupon in coupons.values():
        if check_eligibility(coupon, request.user, request.cart):
            discount = calculate_discount(coupon, request.cart)
            applicable.append({
                "coupon": coupon,
                "discount": discount
            })
    
    if not applicable:
        return {
            "bestCoupon": None,
            "message": "No applicable coupon"
        }
    
    # Sort: highest discount, earliest end date, code name
    applicable.sort(key=lambda x: (-x["discount"], x["coupon"].endDate, x["coupon"].code))
    
    best = applicable[0]
    cart_total = get_cart_total(request.cart)
    
    return {
        "bestCoupon": {
            "couponCode": best["coupon"].code,
            "description": best["coupon"].description,
            "discountType": best["coupon"].discountType,
            "discountAmount": round(best["discount"], 2),
            "finalCartValue": round(cart_total - best["discount"], 2),
            "message": f"Applied {best['coupon'].code}"
        },
        "message": "Best coupon found"
    }
