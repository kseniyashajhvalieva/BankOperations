import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.utils import filter_by_date, get_currency_rates, get_stock_prices, read_excel

logger = logging.getLogger(__name__)


def get_greeting_by_hour(hour: int) -> str:
    """Возвращает приветствие в зависимости от часа."""
    if 5 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def calculate_cards_data(transactions: pd.DataFrame) -> List[Dict[str, Any]]:
    """Рассчитывает данные по картам: расходы и кешбэк."""
    cards_data = []
    expenses = transactions[transactions["Сумма операции"] < 0].copy()

    if not expenses.empty:
        for card in expenses["Номер карты"].dropna().unique():
            card_trans = expenses[expenses["Номер карты"] == card]
            total_spent = abs(card_trans["Сумма операции"].sum())
            cashback = round(total_spent / 100, 2)
            cards_data.append({"last_digits": card[-4:], "total_spent": round(total_spent, 2), "cashback": cashback})

    return cards_data


def get_top_transactions(transactions: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """Возвращает топ-N транзакций по абсолютной сумме."""
    transactions = transactions.copy()
    transactions["abs_amount"] = transactions["Сумма операции"].abs()
    top_n = transactions.nlargest(n, "abs_amount")[
        ["Дата операции", "Сумма операции", "Категория", "Описание"]
    ].to_dict(orient="records")
    return top_n  # type: ignore[return-value]


def load_user_settings() -> Dict[str, Any]:
    """Загружает настройки пользователя из файла."""
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.debug("Настройки пользователя загружены")
        return settings  # type: ignore[no-any-return]
    except FileNotFoundError:
        logger.error("Файл user_settings.json не найден, используются стандартные настройки")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
    except json.JSONDecodeError:
        logger.error("Ошибка парсинга user_settings.json, используются стандартные настройки")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}


def main_page(date_str: str) -> Dict[str, Any]:
    """Главная страница: возвращает JSON с данными за месяц."""
    logger.info(f"Запуск main_page с датой: {date_str}")

    # Загружаем настройки пользователя
    settings = load_user_settings()

    try:
        # Читаем Excel
        df = read_excel("data/operations.xlsx")
        logger.info(f"Загружено {len(df)} транзакций")
    except Exception as e:
        logger.error(f"Ошибка загрузки Excel: {e}")
        return {"error": "Не удалось загрузить данные"}

    try:
        # Определяем период: с 1-го числа месяца по входящую дату
        input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        first_day = input_date.replace(day=1).strftime("%d.%m.%Y")
        end_day = input_date.strftime("%d.%m.%Y")

        df_period = filter_by_date(df, first_day, end_day)
        logger.info(f"Отфильтровано {len(df_period)} транзакций за период {first_day} - {end_day}")
    except Exception as e:
        logger.error(f"Ошибка фильтрации по дате: {e}")
        return {"error": "Ошибка обработки даты"}

    # Приветствие по времени
    greeting = get_greeting_by_hour(input_date.hour)

    # Данные по картам
    cards_data = calculate_cards_data(df_period)

    # Топ-5 транзакций
    top5 = get_top_transactions(df_period, 5)

    # Курсы валют и акции
    try:
        currencies = get_currency_rates(settings["user_currencies"])
        logger.debug(f"Курсы валют: {currencies}")
    except Exception as e:
        logger.error(f"Ошибка получения курсов валют: {e}")
        currencies = [{"currency": c, "rate": 0} for c in settings["user_currencies"]]

    try:
        stocks = get_stock_prices(settings["user_stocks"])
        logger.debug(f"Цены акций: {stocks}")
    except Exception as e:
        logger.error(f"Ошибка получения цен акций: {e}")
        stocks = [{"stock": s, "price": 0} for s in settings["user_stocks"]]

    result = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top5,
        "currency_rates": currencies,
        "stock_prices": stocks,
    }

    logger.info("JSON для главной страницы успешно сформирован")
    return result
