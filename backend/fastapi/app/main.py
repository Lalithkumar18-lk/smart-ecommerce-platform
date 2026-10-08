from datetime import datetime
import hashlib
import hmac
import base64
import json
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr


app = FastAPI(
    title="Smart E-Commerce Platform API",
    description="FastAPI backend for the customer/user panel",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Demo in-memory data
# ---------------------------------------------------------

users = {}

products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "category": "Electronics",
        "price": 2499.00,
        "stock": 25,
        "popularity": 95,
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "category": "Electronics",
        "price": 3999.00,
        "stock": 15,
        "popularity": 90,
    },
    {
        "id": 3,
        "name": "Laptop Backpack",
        "category": "Accessories",
        "price": 1499.00,
        "stock": 40,
        "popularity": 80,
    },
    {
        "id": 4,
        "name": "Running Shoes",
        "category": "Fashion",
        "price": 2999.00,
        "stock": 20,
        "popularity": 85,
    },
]

cart_items = {}
orders = {}
notifications = {}
order_counter = 1001


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CartRequest(BaseModel):
    email: EmailStr
    product_id: int
    quantity: int = 1


class BuyRequest(BaseModel):
    email: EmailStr
    product_id: int
    quantity: int = 1
    payment_method: str = "stripe"


class CheckoutRequest(BaseModel):
    email: EmailStr
    payment_method: str = "stripe"


# ---------------------------------------------------------
# Password helpers
# ---------------------------------------------------------

def hash_password(password: str) -> str:
    salt = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()[:32]

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000,
    )

    return f"{salt}${password_hash.hex()}"


def verify_password(password: str, stored_password: str) -> bool:
    try:
        salt, password_hash = stored_password.split("$", 1)

        calculated = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000,
        ).hex()

        return hmac.compare_digest(calculated, password_hash)

    except Exception:
        return False


# ---------------------------------------------------------
# Simple JWT-style token
# ---------------------------------------------------------

SECRET_KEY = "smart-ecommerce-demo-secret-key"


def create_token(email: str) -> str:
    payload = {
        "email": email,
        "exp": int(time.time()) + 86400,
    }

    payload_text = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    payload_encoded = base64.urlsafe_b64encode(
        payload_text
    ).decode()

    signature = hmac.new(
        SECRET_KEY.encode(),
        payload_encoded.encode(),
        hashlib.sha256,
    ).hexdigest()

    return f"{payload_encoded}.{signature}"


def get_email_from_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Use Bearer token",
        )

    token = authorization.replace("Bearer ", "", 1)

    try:
        payload_encoded, signature = token.split(".", 1)

        expected_signature = hmac.new(
            SECRET_KEY.encode(),
            payload_encoded.encode(),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(
            signature,
            expected_signature,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

        payload = json.loads(
            base64.urlsafe_b64decode(
                payload_encoded.encode()
            )
        )

        if payload["exp"] < int(time.time()):
            raise HTTPException(
                status_code=401,
                detail="Token expired",
            )

        return payload["email"]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


# ---------------------------------------------------------
# Root / health
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Smart E-Commerce Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "smart-ecommerce-platform",
    }


# ---------------------------------------------------------
# Products
# ---------------------------------------------------------

@app.get("/products")
def get_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
):
    result = products.copy()

    if category:
        result = [
            p for p in result
            if p["category"].lower() == category.lower()
        ]

    if max_price is not None:
        result = [
            p for p in result
            if p["price"] <= max_price
        ]

    return {
        "products": result,
        "count": len(result),
    }


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

@app.post("/register")
@app.post("/auth/register")
def register_user(data: RegisterRequest):
    email = str(data.email).lower()

    if email in users:
        raise HTTPException(
            status_code=400,
            detail="User already exists",
        )

    users[email] = {
        "name": data.name,
        "email": email,
        "password": hash_password(data.password),
        "role": "customer",
    }

    notifications[email] = []

    return {
        "message": "Registration successful",
        "user": {
            "name": data.name,
            "email": email,
            "role": "customer",
        },
    }


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.post("/login")
@app.post("/auth/login")
def login_user(data: LoginRequest):
    email = str(data.email).lower()

    user = users.get(email)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        data.password,
        user["password"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_token(email)

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }


# ---------------------------------------------------------
# Add to cart
# ---------------------------------------------------------

@app.post("/cart")
def add_to_cart(data: CartRequest):
    email = str(data.email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    product = next(
        (
            p for p in products
            if p["id"] == data.product_id
        ),
        None,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    if data.quantity > product["stock"]:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    if email not in cart_items:
        cart_items[email] = []

    existing = next(
        (
            item
            for item in cart_items[email]
            if item["product_id"] == data.product_id
        ),
        None,
    )

    if existing:
        existing["quantity"] += data.quantity
    else:
        cart_items[email].append(
            {
                "product_id": data.product_id,
                "quantity": data.quantity,
            }
        )

    return {
        "message": "Product added to cart",
        "cart": cart_items[email],
    }


# ---------------------------------------------------------
# View cart
# ---------------------------------------------------------

@app.get("/cart")
def get_cart(email: EmailStr):
    email = str(email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    items = []
    total = 0.0

    for item in cart_items.get(email, []):
        product = next(
            (
                p for p in products
                if p["id"] == item["product_id"]
            ),
            None,
        )

        if product:
            subtotal = (
                product["price"] *
                item["quantity"]
            )

            items.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                    "subtotal": subtotal,
                }
            )

            total += subtotal

    return {
        "items": items,
        "total": total,
    }


# ---------------------------------------------------------
# Buy Now
# ---------------------------------------------------------

@app.post("/buy")
def buy_now(data: BuyRequest):
    global order_counter

    email = str(data.email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    product = next(
        (
            p for p in products
            if p["id"] == data.product_id
        ),
        None,
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if data.quantity > product["stock"]:
        raise HTTPException(
            status_code=400,
            detail="Insufficient stock",
        )

    total = product["price"] * data.quantity

    order_id = order_counter
    order_counter += 1

    orders[order_id] = {
        "id": order_id,
        "email": email,
        "items": [
            {
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": data.quantity,
                "unit_price": product["price"],
            }
        ],
        "total": total,
        "payment_method": data.payment_method,
        "payment_status": "paid",
        "order_status": "placed",
        "created_at": datetime.now().isoformat(),
        "history": [
            {
                "status": "placed",
                "message": "Order placed successfully",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "status": "paid",
                "message": "Payment successful",
                "timestamp": datetime.now().isoformat(),
            },
        ],
    }

    product["stock"] -= data.quantity

    if email not in notifications:
        notifications[email] = []

    notifications[email].append(
        {
            "type": "order",
            "message": (
                f"Order #{order_id} placed successfully"
            ),
            "read": False,
            "created_at": datetime.now().isoformat(),
        }
    )

    return {
        "message": "Order placed successfully",
        "order": orders[order_id],
    }


# ---------------------------------------------------------
# Checkout Cart
# ---------------------------------------------------------

@app.post("/checkout")
def checkout(data: CheckoutRequest):
    global order_counter

    email = str(data.email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user_cart = cart_items.get(email, [])

    if not user_cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty",
        )

    order_items = []
    total = 0.0

    for item in user_cart:
        product = next(
            (
                p for p in products
                if p["id"] == item["product_id"]
            ),
            None,
        )

        if not product:
            continue

        if item["quantity"] > product["stock"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product['name']}",
            )

        subtotal = (
            product["price"] *
            item["quantity"]
        )

        total += subtotal

        order_items.append(
            {
                "product_id": product["id"],
                "product_name": product["name"],
                "quantity": item["quantity"],
                "unit_price": product["price"],
            }
        )

    order_id = order_counter
    order_counter += 1

    orders[order_id] = {
        "id": order_id,
        "email": email,
        "items": order_items,
        "total": total,
        "payment_method": data.payment_method,
        "payment_status": "paid",
        "order_status": "placed",
        "created_at": datetime.now().isoformat(),
        "history": [
            {
                "status": "placed",
                "message": "Order placed successfully",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "status": "paid",
                "message": "Payment successful",
                "timestamp": datetime.now().isoformat(),
            },
        ],
    }

    for item in user_cart:
        product = next(
            (
                p for p in products
                if p["id"] == item["product_id"]
            ),
            None,
        )

        if product:
            product["stock"] -= item["quantity"]

    cart_items[email] = []

    if email not in notifications:
        notifications[email] = []

    notifications[email].append(
        {
            "type": "order",
            "message": (
                f"Order #{order_id} confirmed. "
                f"Payment successful."
            ),
            "read": False,
            "created_at": datetime.now().isoformat(),
        }
    )

    return {
        "message": "Checkout successful",
        "order": orders[order_id],
    }


# ---------------------------------------------------------
# Order History
# ---------------------------------------------------------

@app.get("/orders")
def get_orders(email: EmailStr):
    email = str(email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user_orders = [
        order
        for order in orders.values()
        if order["email"] == email
    ]

    return {
        "orders": user_orders,
        "count": len(user_orders),
    }


@app.get("/orders/{order_id}")
def get_order(
    order_id: int,
    email: EmailStr,
):
    email = str(email).lower()

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order["email"] != email:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this order",
        )

    return order


# ---------------------------------------------------------
# Order tracking / history
# ---------------------------------------------------------

@app.get("/orders/{order_id}/history")
def get_order_history(
    order_id: int,
    email: EmailStr,
):
    email = str(email).lower()

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order["email"] != email:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this order",
        )

    return {
        "order_id": order_id,
        "history": order["history"],
    }


# ---------------------------------------------------------
# Notifications
# ---------------------------------------------------------

@app.get("/notifications")
def get_notifications(email: EmailStr):
    email = str(email).lower()

    if email not in users:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "notifications": notifications.get(email, []),
        "count": len(
            notifications.get(email, [])
        ),
    }


# ---------------------------------------------------------
# Demo payment confirmation
# ---------------------------------------------------------

@app.post("/payment/{order_id}")
def process_payment(
    order_id: int,
    email: EmailStr,
):
    email = str(email).lower()

    order = orders.get(order_id)

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    if order["email"] != email:
        raise HTTPException(
            status_code=403,
            detail="You cannot access this order",
        )

    order["payment_status"] = "paid"

    order["history"].append(
        {
            "status": "paid",
            "message": "Payment successful",
            "timestamp": datetime.now().isoformat(),
        }
    )

    if email not in notifications:
        notifications[email] = []

    notifications[email].append(
        {
            "type": "payment",
            "message": (
                f"Payment successful for Order #{order_id}"
            ),
            "read": False,
            "created_at": datetime.now().isoformat(),
        }
    )

    return {
        "message": "Payment successful",
        "order_id": order_id,
        "payment_status": "paid",
    }

from app.stripe_payments import router as stripe_payments_router
app.include_router(stripe_payments_router)
from app.demo_payment import router as demo_payment_router
app.include_router(demo_payment_router)
