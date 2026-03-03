from abc import ABC, abstractmethod
from typing import Any

from app.models import Task


class PaymentProvider(ABC):
    @abstractmethod
    def create_invoice(self, task: Task) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(self, payload: bytes, headers: dict[str, str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_status(self, invoice_id: str) -> str:
        raise NotImplementedError


class StubPaymentProvider(PaymentProvider):
    def create_invoice(self, task: Task) -> dict[str, Any]:
        return {
            "invoice_id": f"stub-{task.id}",
            "pay_url": None,
            "status": "NOT_IMPLEMENTED",
        }

    def verify_webhook(self, payload: bytes, headers: dict[str, str]) -> bool:
        return False

    def get_status(self, invoice_id: str) -> str:
        return "NOT_IMPLEMENTED"
