import os
from datetime import datetime, timezone
from decimal import Decimal
from itertools import count
from threading import RLock
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StringConstraints

VERSION = os.getenv("APP_VERSION", "v1.0-prod-bundle")
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]

class PaymentInput(BaseModel):
    payer: Name
    payee: Name
    amount: Decimal = Field(gt=0, decimal_places=2, allow_inf_nan=False)
    currency: Literal["INR", "USD", "EUR"]

def create_app():
    app = FastAPI(title="Enterprise Payment & Notification Engine", version=VERSION)
    origins = [s.strip() for s in os.getenv("CORS_ORIGINS", "").split(",") if s.strip()]
    if origins:
        app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
    lock = RLock()
    ids = count(4)
    payments = [dict(id=i, payer=payer, payee=payee, amount=amount, currency="INR", status=status,
                     created_at=f"2026-01-01T00:00:0{i}+00:00")
                for i, payer, payee, amount, status in [
                    (1, "Asha", "Northwind", "1250.00", "COMPLETED"),
                    (2, "Ravi", "Contoso", "890.50", "PENDING"),
                    (3, "Mira", "Fabrikam", "420.00", "FAILED")]]
    notifications = [dict(id=i, payment_id=i, message=f"Payment #{i}: {p['status']}", created_at=p['created_at'])
                     for i, p in reversed(list(enumerate(payments, 1)))]

    @app.get("/")
    @app.get("/health")
    def health():
        return {"status": "healthy", "version": VERSION}

    @app.get("/api/payments")
    def list_payments():
        with lock:
            return list(reversed(payments))

    @app.get("/api/payments/{payment_id}")
    def get_payment(payment_id: int):
        with lock:
            for payment in payments:
                if payment['id'] == payment_id:
                    return payment
        raise HTTPException(status_code=404, detail="Payment not found")

    @app.post("/api/payments", status_code=201)
    def create_payment(payload: PaymentInput):
        with lock:
            payment = dict(id=next(ids), **payload.model_dump(exclude={'amount'}), amount=format(payload.amount, '.2f'),
                           status="PENDING", created_at=datetime.now(timezone.utc).isoformat())
            payments.append(payment)
            notifications.insert(0, dict(id=payment['id'], payment_id=payment['id'],
                                        message=f"Payment #{payment['id']} created for {payment['currency']} {payment['amount']}",
                                        created_at=payment['created_at']))
            return payment

    @app.get("/api/notifications")
    def list_notifications():
        with lock:
            return list(notifications)
    return app

app = create_app()
