"""
Task 5.2: Idempotency Keys for Payment Processing

Implements idempotency handling for payment systems to ensure payments aren't duplicated.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from threading import Lock
import hashlib
import uuid
import time


class PaymentState(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Payment:
    payment_id: str
    idempotency_key: str
    amount: float
    currency: str
    description: str
    state: PaymentState = PaymentState.PENDING
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
            self.completed_at = None


@dataclass
class IdempotencyKey:
    key: str
    expires_at: datetime
    is_expired: bool = False
    
    def __post_init__(self):
        self.is_expired = self.expires_at < datetime.now()


class PaymentService:
    """
    Payment service with idempotency key management.
    
    Ensures:
    - Same payment request doesn't create duplicate payments
    - Failed operations can be safely retried
    - Concurrent requests are handled safely
    """
    
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
        self._idempotency_keys: Dict[str, IdempotencyKey] = {}
        self._lock = Lock()
        self._payment_callbacks: list = []
    
    def process_payment(
        self,
        user_id: Optional[str] = None,
        amount: float = 0,
        currency: str = "USD",
        description: str = "",
        idempotency_key: Optional[str] = None,
        **kwargs
    ) -> Payment:
        """
        Process a payment with idempotency protection.
        
        Args:
            idempotency_key: Unique key to prevent duplicate payments
            amount: Payment amount
            currency: Currency code
            description: Payment description
        
        Returns:
            Payment object
            
        Raises:
            ValueError: If payment parameters are invalid
        """
        # Validate parameters
        if amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        # Check for existing idempotent payment
        with self._lock:
            if idempotency_key in self._payments:
                return self._payments[idempotency_key]
            
            # Create new payment
            payment = Payment(
                payment_id=str(uuid.uuid4()),
                idempotency_key=idempotency_key,
                amount=amount,
                currency=currency,
                description=description,
                state=PaymentState.PENDING,
                created_at=datetime.now()
            )
            
            # Create idempotency key
            expires_at = datetime.now() + timedelta(hours=24)
            idempotency_key_obj = IdempotencyKey(
                key=idempotency_key,
                expires_at=expires_at
            )
            
            self._idempotency_keys[idempotency_key] = idempotency_key_obj
            self._payments[idempotency_key] = payment
        
        try:
            # Process the payment
            payment.state = PaymentState.PROCESSING
            result = self._execute_payment(payment)
            
            payment.state = PaymentState.COMPLETED
            payment.completed_at = datetime.now()
            return result
            
        except Exception as e:
            payment.state = PaymentState.FAILED
            raise
    
    def is_payment_completed(self, idempotency_key: str) -> bool:
        """Check if payment with key is completed."""
        payment = self._payments.get(idempotency_key)
        return payment is not None and payment.state == PaymentState.COMPLETED
    
    def _execute_payment(self, payment: Payment) -> Payment:
        """Execute the actual payment processing."""
        # In real implementation, this would call payment processor
        return payment
    
    def get_payment_status(self, idempotency_key: str) -> Optional[Payment]:
        """Get payment status by idempotency key."""
        return self._payments.get(idempotency_key)
    
    def is_payment_completed(self, idempotency_key: str) -> bool:
        """Check if payment with key is completed."""
        payment = self._payments.get(idempotency_key)
        return payment and payment.state == PaymentState.COMPLETED
    
    def add_callback(self, callback):
        """Add a payment processing callback."""
        self._payment_callbacks.append(callback)
    
    def process_callbacks(self, payment: Payment):
        """Process callbacks for a payment."""
        for callback in self._payment_callbacks:
            try:
                callback(payment)
            except Exception as e:
                pass


def test_idempotency_keys():
    """Test idempotency key functionality."""
    service = PaymentService()
    
    # Test successful payment
    payment1 = service.process_payment(
        idempotency_key="pay-001",
        amount=100.00,
        description="Test payment"
    )
    assert payment1.amount == 100.00
    assert payment1.state == PaymentState.COMPLETED
    
    # Test duplicate payment - should return same payment
    payment2 = service.process_payment(
        idempotency_key="pay-001",
        amount=100.00,
        description="Test payment"
    )
    assert payment1.payment_id == payment2.payment_id
    
    # Test different idempotency key - should create new payment
    payment3 = service.process_payment(
        idempotency_key="pay-002",
        amount=50.00,
        description="Different payment"
    )
    assert payment3.amount == 50.00
    assert payment1.payment_id != payment3.payment_id
    
    # Test invalid parameters
    try:
        service.process_payment(
            idempotency_key="pay-003",
            amount=-100.00,
            description="Negative amount"
        )
    except ValueError:
        pass
    
    # Test payment status retrieval
    status = service.get_payment_status("pay-001")
    assert status is not None
    assert status.state == PaymentState.COMPLETED
    
    # Test callback functionality
    payment_success = False
    def callback_handler(payment):
        nonlocal payment_success
        payment_success = True
    
    service.add_callback(callback_handler)
    service.process_payment(
        idempotency_key="pay-004",
        amount=75.00,
        description="Callback test"
    )
    service.process_callbacks(Payment(
        payment_id="test",
        idempotency_key="test",
        amount=75.00,
        currency="USD",
        description="Callback test"
    ))
    
    print("Tests passed")

if __name__ == "__main__":
    test_idempotency_keys()
