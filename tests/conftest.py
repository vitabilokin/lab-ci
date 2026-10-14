import pytest

from shop.cart import Cart


@pytest.fixture
def empty_cart() -> Cart:
    """Порожній кошик."""
    return Cart()


@pytest.fixture
def cart_with_items() -> Cart:
    """Кошик із двома товарами: 2 книги по 200 і 4 ручки по 15 (разом 460 грн)."""
    cart = Cart()
    cart.add("book", price=200.0, qty=2)
    cart.add("pen", price=15.0, qty=4)
    return cart
