import os
import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/payments", tags=["Payments"])

class CheckoutRequest(BaseModel):
    email: str
    product_name: str
    amount_inr: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1, le=100)
    method: str = "stripe"

@router.post("/checkout")
def checkout(data: CheckoutRequest):
    if data.method == "cod":
        return {
            "method": "cod",
            "status": "pending",
            "message": "Cash on Delivery selected."
        }

    if data.method != "stripe":
        raise HTTPException(status_code=400, detail="Invalid payment method")

    key = os.getenv("STRIPE_SECRET_KEY")
    if not key:
        raise HTTPException(
            status_code=503,
            detail="Set your Stripe TEST secret key first."
        )

    stripe.api_key = key

    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=data.email,
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": data.product_name},
                    "unit_amount": data.amount_inr * 100
                },
                "quantity": data.quantity
            }],
            success_url="http://localhost:5173/?payment=success",
            cancel_url="http://localhost:5173/?payment=cancelled"
        )
        return {"checkout_url": session.url}
    except Exception:
        raise HTTPException(status_code=502, detail="Stripe checkout failed")
