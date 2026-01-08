from order_processing import process_checkout

# Тест 1
result1 = process_checkout({
    "user_id": 1,
    "items": [{"price": 50, "qty": 2}],
    "coupon": None,
    "currency": "USD"
})
print("Тест 1:", result1)
print("Сумма должна быть 121:", result1["total"] == 121)

# Тест 2
result2 = process_checkout({
    "user_id": 2,
    "items": [{"price": 100, "qty": 3}],
    "coupon": "SAVE10",
    "currency": "EUR"
})
print("\nТест 2:", result2)
