from typing import Optional, Tuple

import stripe

from online_school.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_product(name: str) -> dict:
    """Создает продукт в страйпе."""
    return stripe.Product.create(name=name)


def create_stripe_price(payment_amount: int, product_id: str) -> dict:
    """Создает цену в страйпе."""
    return stripe.Price.create(
        currency="rub",
        unit_amount=payment_amount * 100,
        product=product_id,
    )


def create_stripe_session(price: str) -> Tuple[Optional[str], Optional[str]]:
    """Создает сессию в страйпе."""
    session = stripe.checkout.Session.create(
        success_url="https://example.com/success",
        line_items=[{"price": price, "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


def retrieve_stripe_session(session_id: str) -> Optional[dict]:
    """Проверяет статус сессии в страйпе."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return session
    except stripe.error.InvalidRequestError:
        return None
