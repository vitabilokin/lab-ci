from unittest.mock import Mock

import pytest

from shop.cart import Cart, Item


def test_empty_cart_has_no_items(empty_cart: Cart) -> None:
    assert empty_cart.items_count() == 0
    assert empty_cart.total() == 0


def test_add_single_item_default_qty(empty_cart: Cart) -> None:
    empty_cart.add("book", price=100.0)
    assert empty_cart.items_count() == 1


def test_items_count(cart_with_items: Cart) -> None:
    assert cart_with_items.items_count() == 6


def test_add_same_item_twice_increases_qty(empty_cart: Cart) -> None:
    empty_cart.add("book", price=100.0, qty=1)
    empty_cart.add("book", price=100.0, qty=2)
    assert empty_cart.items_count() == 3
    assert empty_cart.total() == 300.0


def test_add_same_name_with_other_price_keeps_first_price(empty_cart: Cart) -> None:
    empty_cart.add("book", price=100.0, qty=1)
    empty_cart.add("book", price=999.0, qty=1)
    assert empty_cart.total() == 200.0


def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price"):
        empty_cart.add("book", price=-1.0)


@pytest.mark.parametrize("qty", [0, -1])
def test_add_non_positive_qty_raises(empty_cart: Cart, qty: int) -> None:
    with pytest.raises(ValueError, match="qty"):
        empty_cart.add("book", price=10.0, qty=qty)


def test_add_zero_price_is_allowed(empty_cart: Cart) -> None:
    empty_cart.add("gift", price=0.0)
    assert empty_cart.total() == 0


@pytest.mark.parametrize("discount", [-1, -0.01, 100.01, 150])
def test_invalid_discount_raises(cart_with_items: Cart, discount: float) -> None:
    with pytest.raises(ValueError, match="discount"):
        cart_with_items.total(discount_percent=discount)


def test_remove_missing_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("ghost")


def test_remove_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("pen")
    assert cart_with_items.items_count() == 2
    assert cart_with_items.total() == 400.0


@pytest.mark.parametrize(
    ("discount", "expected"),
    [(0, 460.0), (10, 414.0), (50, 230.0), (99.99, 0.05), (100, 0.0)],
)
def test_total_with_discount(cart_with_items: Cart, discount: float, expected: float) -> None:
    assert cart_with_items.total(discount_percent=discount) == pytest.approx(expected)


def test_total_rounds_to_two_decimals(empty_cart: Cart) -> None:
    empty_cart.add("a", price=0.1)
    empty_cart.add("b", price=0.2)
    assert empty_cart.total() == 0.3


def test_total_in_usd_with_mock(cart_with_items: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0

    assert cart_with_items.total_in("USD", rates) == 11.5
    rates.get_rate.assert_called_once_with("USD")


class FakeRates:
    def __init__(self, rates: dict[str, float]) -> None:
        self._rates = rates

    def get_rate(self, currency: str) -> float:
        return self._rates[currency]


def test_total_in_eur_with_stub(cart_with_items: Cart) -> None:
    rates = FakeRates({"EUR": 46.0})
    assert cart_with_items.total_in("EUR", rates) == 10.0


@pytest.mark.parametrize("rate", [0.0, -5.0])
def test_total_in_invalid_rate_raises(cart_with_items: Cart, rate: float) -> None:
    rates = Mock()
    rates.get_rate.return_value = rate
    with pytest.raises(ValueError, match="rate"):
        cart_with_items.total_in("USD", rates)


def test_most_expensive_empty_cart_returns_none(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_returns_item_with_max_unit_price(cart_with_items: Cart) -> None:
    item = cart_with_items.most_expensive()
    assert item == Item("book", 200.0, 2)


def test_most_expensive_uses_unit_price_not_sum(empty_cart: Cart) -> None:
    empty_cart.add("pen", price=15.0, qty=100)
    empty_cart.add("book", price=200.0, qty=1)
    item = empty_cart.most_expensive()
    assert item is not None
    assert item.name == "book"
