import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()


def read_excel(filepath: str) -> pd.DataFrame:
    """Читает Excel-файл с транзакциями."""
    df = pd.read_excel(filepath)
    # Преобразуем строку с датой в тип datetime для фильтрации
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format='%d.%m.%Y %H:%M:%S')
    return df


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Фильтрует транзакции по дате."""
    # Формат даты: 'DD.MM.YYYY'
    start_date = pd.to_datetime(start, format='%d.%m.%Y')
    end_date = pd.to_datetime(end, format='%d.%m.%Y')

    mask = (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    return df.loc[mask]


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает курсы валют через API (бесплатно, без ключа)."""
    rates = []
    url = "https://api.exchangerate-api.com/v4/latest/RUB"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        for currency in currencies:
            rate = data["rates"].get(currency, 0)
            rates.append({"currency": currency, "rate": round(rate, 2)})
    except Exception as e:
        print(f"Ошибка получения курсов: {e}")
        # Если API недоступен, возвращаем нули
        for currency in currencies:
            rates.append({"currency": currency, "rate": 0})

    return rates


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает цены акций через API (требуется ключ в .env)."""
    api_key = os.getenv("STOCK_API_KEY")
    prices = []

    if not api_key:
        print("Нет API-ключа для акций")
        return [{"stock": s, "price": 0} for s in stocks]

    for stock in stocks:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Alpha Vantage возвращает цену в поле "05. price"
            price = float(data.get("Global Quote", {}).get("05. price", 0))
            prices.append({"stock": stock, "price": round(price, 2)})
        except Exception as e:
            print(f"Ошибка для {stock}: {e}")
            prices.append({"stock": stock, "price": 0})

    return prices
