"""
Обработка заказов с чистой архитектурой
"""

# Константы
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_PRICE = 0
MIN_QUANTITY = 0

# Коды скидок и их параметры
COUPON_DISCOUNTS = {
    "SAVE10": {"type": "percentage", "value": 0.10},
    "SAVE20": {"type": "tiered", "threshold": 200, "high_rate": 0.20, "low_rate": 0.05},
    "VIP": {"type": "fixed_tiered", "base_discount": 50, "min_threshold": 100, "low_discount": 10}
}


def parse_order_request(request: dict) -> tuple:
    """Извлекает и возвращает данные из запроса."""
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency")
    )


def validate_order_data(user_id, items, currency) -> None:
    """Проверяет корректность данных заказа."""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    
    validate_items(items)
    
    if currency is None:
        raise ValueError("currency is required")


def validate_items(items: list) -> None:
    """Проверяет корректность каждого товара в заказе."""
    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= MIN_PRICE:
            raise ValueError("price must be positive")
        if item["qty"] <= MIN_QUANTITY:
            raise ValueError("qty must be positive")


def calculate_subtotal(items: list) -> int:
    """Вычисляет общую сумму заказа до скидок."""
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(subtotal: int, coupon: str) -> int:
    """Вычисляет размер скидки на основе купона."""
    if not coupon:
        return 0
    
    if coupon not in COUPON_DISCOUNTS:
        raise ValueError("unknown coupon")
    
    discount_config = COUPON_DISCOUNTS[coupon]
    
    if discount_config["type"] == "percentage":
        return int(subtotal * discount_config["value"])
    
    elif discount_config["type"] == "tiered":
        rate = (discount_config["high_rate"] if subtotal >= discount_config["threshold"]
                else discount_config["low_rate"])
        return int(subtotal * rate)
    
    elif discount_config["type"] == "fixed_tiered":
        return (discount_config["base_discount"] if subtotal >= discount_config["min_threshold"]
                else discount_config["low_discount"])
    
    return 0


def calculate_tax(amount: int) -> int:
    """Вычисляет налог на указанную сумму."""
    return int(amount * TAX_RATE)


def generate_order_id(user_id: int, items_count: int) -> str:
    """Генерирует уникальный идентификатор заказа."""
    return f"{user_id}-{items_count}-X"


def apply_discount(subtotal: int, discount: int) -> int:
    """Применяет скидку к сумме, гарантируя неотрицательный результат."""
    total = subtotal - discount
    return max(total, 0)


def process_checkout(request: dict) -> dict:
    """Основная функция обработки заказа."""
    # Шаг 1: Извлечение данных
    user_id, items, coupon, currency = parse_order_request(request)
    
    # Шаг 2: Валидация
    validate_order_data(user_id, items, currency)
    
    # Шаг 3: Расчет промежуточных значений
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)
    total_after_discount = apply_discount(subtotal, discount)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    
    # Шаг 4: Формирование результата
    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
