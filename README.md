# Simple Coupon System

E-commerce coupon management system built with FastAPI. Create coupons with complex eligibility rules and automatically find the best discount for users.

## ⚡ Quick Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run
uvicorn main:app --reload
```

Visit: **http://localhost:8000/docs**

##  Demo Credentials

**IMPORTANT:** Use these credentials for login

```
Email: hire-me@anshumat.org
Password: HireMe@2025!
```

##  Features

-  Create coupons with eligibility rules (user tier, spend history, cart value, categories)
-  Automatically find best applicable coupon (highest discount → earliest expiry → code)
-  JWT authentication with bcrypt password hashing
-  In-memory storage (no database required)
-  Support for FLAT and PERCENT discount types
-  Usage limits per user
-  Date-based coupon validity

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and demo credentials |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/coupons/` | Create new coupon |
| GET | `/coupons/` | Get all coupons |
| POST | `/coupons/best` | Find best coupon for user & cart |

## Tech Stack

- **Python** 3.10+
- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **JWT (python-jose)** - Authentication tokens
- **Bcrypt (passlib)** - Password hashing
- **Uvicorn** - ASGI server

## Eligibility Rules Supported

### User-based Rules
- **User Tier**: NEW, REGULAR, GOLD
- **Minimum Lifetime Spend**: Total amount spent by user
- **Minimum Orders Placed**: Number of previous orders
- **First Order Only**: Coupon valid only for first purchase
- **Allowed Countries**: Country restriction (e.g., IN, US)

### Cart-based Rules
- **Minimum Cart Value**: Minimum order amount required
- **Applicable Categories**: Coupon applies to specific categories only
- **Excluded Categories**: Coupon doesn't apply if cart contains these
- **Minimum Items Count**: Minimum number of items in cart

## Coupon Selection Logic

When finding the best coupon, the system:

1. **Filters** all coupons by:
   - Valid date range (current date between startDate and endDate)
   - User hasn't exceeded usage limit
   - User meets all eligibility criteria
   - Cart meets all eligibility criteria

2. **Calculates** discount for each eligible coupon:
   - **FLAT**: Direct amount off (e.g., ₹100 off)
   - **PERCENT**: Percentage off with optional max cap (e.g., 20% off, max ₹500)

3. **Selects** best coupon using priority:
   -  Highest discount amount
   -  If tie → Earliest end date
   -  If still tie → Lexicographically smaller code

##  API Examples

### 1. Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "hire-me@anshumat.org",
  "password": "HireMe@2025!"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Create Coupon

```bash
POST /coupons/
Content-Type: application/json

{
  "code": "SAVE100",
  "description": "Save ₹100 on orders above ₹500",
  "discountType": "FLAT",
  "discountValue": 100,
  "startDate": "2025-01-01T00:00:00",
  "endDate": "2025-12-31T23:59:59",
  "usageLimitPerUser": 1,
  "eligibility": {
    "minCartValue": 500
  }
}
```

### 3. Get All Coupons

```bash
GET /coupons/
```

### 4. Find Best Coupon

```bash
POST /coupons/best
Content-Type: application/json

{
  "user": {
    "userId": "u123",
    "userTier": "NEW",
    "country": "IN",
    "lifetimeSpend": 0,
    "ordersPlaced": 0
  },
  "cart": {
    "items": [
      {
        "productId": "p1",
        "category": "electronics",
        "unitPrice": 1500,
        "quantity": 1
      },
      {
        "productId": "p2",
        "category": "fashion",
        "unitPrice": 500,
        "quantity": 2
      }
    ]
  }
}
```

**Response:**
```json
{
  "bestCoupon": {
    "couponCode": "WELCOME100",
    "description": "Welcome offer",
    "discountType": "FLAT",
    "discountAmount": 100.0,
    "finalCartValue": 2400.0,
    "message": "Applied WELCOME100"
  },
  "message": "Best coupon found"
}
```

## 🏗️ Project Structure

```
coupon-system/
├── main.py              # FastAPI app with all APIs
├── models.py            # Pydantic models for data validation
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

##  Pre-loaded Coupons

The system comes with a sample coupon:

**WELCOME100**
- Type: FLAT ₹100 off
- For: NEW users only
- Minimum cart: ₹500
- First order only
- Usage limit: 1 per user
- Valid: Jan 1, 2025 - Dec 31, 2025

##  Testing

You can test the API using:

1. **Swagger UI**: http://localhost:8000/docs
2. **cURL**: See API examples above
3. **Postman**: Import endpoints from Swagger
4. **Python requests library**

### Example cURL Test

```bash
# Test best coupon endpoint
curl -X POST "http://localhost:8000/coupons/best" \
  -H "Content-Type: application/json" \
  -d '{
    "user": {
      "userId": "u123",
      "userTier": "NEW",
      "country": "IN",
      "lifetimeSpend": 0,
      "ordersPlaced": 0
    },
    "cart": {
      "items": [{
        "productId": "p1",
        "category": "electronics",
        "unitPrice": 1500,
        "quantity": 1
      }]
    }
  }'
```

## Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Troubleshooting

### bcrypt Error
```bash
pip install bcrypt
```

### Port Already in Use
```bash
# Change port
uvicorn main:app --reload --port 8001
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```


** If you found this helpful, please star the repository!**