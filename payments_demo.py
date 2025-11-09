# app/payments.py
import os
from fastapi import HTTPException

PAYMENT_SECRET = os.getenv("PAYMENT_SECRET", "dummy")

def create_checkout_session(user_id: int, amount: int, resume_id: int):
    """
    Stub: In production, call Cashfree/Instamojo SDK to create session/payment link.
    Return: { "payment_url": "...", "payment_id": "..." }
    """
    # Simulate checkout link
    return {
        "payment_url": f"https://pay.example.com/checkout?user={user_id}&resume={resume_id}&amount={amount}",
        "payment_id": f"pay_{user_id}_{resume_id}"
    }

def verify_payment(payment_id: str):
    # In production, query gateway for status or process webhooks
    # Here we mock success
    if not payment_id:
        raise HTTPException(status_code=400, detail="missing payment id")
    return {"status": "SUCCESS", "payment_id": payment_id}

