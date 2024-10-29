import requests

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Логика конвертации валюты с использованием внешнего API.
    """
    if amount <= 0:
        raise ValueError("Сумма должна быть положительным числом")

    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Ошибка при запросе курса валют: {response.status_code}")

    data = response.json()
    exchange_rate = data["rates"].get(to_currency)

    if exchange_rate is None:
        raise ValueError(f"Валюта {to_currency} не найдена в курсе валют {from_currency}")

    return round(amount * exchange_rate, 2)


def convert_currency_from_openapi(amount: float, from_currency: str, to_currency: str) -> float:
    if amount <= 0:
        raise ValueError("Сумма должна быть положительным числом")

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@2024.10.12/v1/currencies/{from_currency.lower()}.json"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Ошибка запроса: {response.status_code}")
    
    data = response.json()

    exchange_rate = data.get(from_currency.lower(), {}).get(to_currency.lower())
    
    if exchange_rate is None:
        exchange_rate = data.get(from_currency.lower(), {}).get(to_currency.lower())
    
    if exchange_rate is None:
        raise ValueError(f"Не удалось найти курс для валюты {to_currency.lower()}")

    return round(amount * exchange_rate, 2)
