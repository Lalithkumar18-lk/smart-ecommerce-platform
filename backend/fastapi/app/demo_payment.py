from fastapi import APIRouter
from pydantic import BaseModel
from uuid import uuid4

router = APIRouter(prefix="/demo-payment", tags=["Demo Payment"])

class PaymentRequest(BaseModel):
    product_name: str
    amount: float
    method: str = "card"
    simulate: str = "success"

@router.post("/pay")
def demo_pay(data: PaymentRequest):
    if data.amount <= 0:
        return {"status": "failed", "message": "Invalid amount"}

    if data.simulate == "failure":
        return {
            "status": "failed",
            "message": "Demo payment declined. Try again."
        }

    return {
        "status": "success",
        "payment_id": "DEMO-" + uuid4().hex[:10].upper(),
        "product": data.product_name,
        "amount": data.amount,
        "method": data.method,
        "message": "Demo payment successful. No real money charged."
    }
