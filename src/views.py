import json
import logging
from datetime import datetime
from typing import Any, Dict

import pandas as pd

from src.utils import (
    filter_by_date,
    get_currency_rates,
    get_stock_prices,
    read_excel,
)

logger = logging.getLogger(__name__)


def main_page(date_str: str) -> Dict[str, Any]:
    """Главная страница: возвращает JSON с данными за месяц."""
    # Загружаем настройки пользователя
    with open("user_settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    # Читаем Excel
    df = read_excel("data/operations.xlsx")

    # Определяем период: с 1-го числа месяца по входящую дату
    input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    first_day = input_date.replace(day=1).strftime("%d.%m.%Y")
    end_day = input_date.strftime("%d.%m.%Y")

    df_period = filter_by_date(df, first_day, end_day)

    # Приветствие по времени
    hour = input_date.hour
    if 5 <= hour < 12:
        greeting = "Доброе утро"
    elif 12 <= hour < 18:
        greeting = "Добрый день"
    elif 18 <= hour < 23:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"

    # Данные по картам (расходы и кешбэк)
    cards_data = []
    # Только расходы (отрицательные суммы)
    expenses = df_period[df_period["Сумма операции"] < 0].copy()
    if not expenses.empty:
        for card in expenses["Номер карты"].dropna().unique():
            card_trans = expenses[expenses["Номер карты"] == card]
            total_spent = abs(card_trans["Сумма операции"].sum())
            cashback = round(total_spent / 100, 2)  # 1 рубль на каждые 100
            cards_data.append(
                {"last_digits": card[-4:], "total_spent": round(total_spent, 2), "cashback": cashback}
            )

    # Топ-5 транзакций по сумме (по модулю, любые операции)
    df_period["abs_amount"] = df_period["Сумма операции"].abs()
    top5 = df_period.nlargest(5, "abs_amount")[
        ["Дата операции", "Сумма операции", "Категория", "Описание"]
    ].to_dict(orient="records")

    # Курсы валют и акции
    currencies = get_currency_rates(settings["user_currencies"])
    stocks = get_stock_prices(settings["user_stocks"])

    result = {
        "greeting": greeting,
        "cards": cards_data,
        "top_transactions": top5,
        "currency_rates": currencies,
        "stock_prices": stocks,
    }

    logger.info("JSON для главной страницы успешно сформирован")
    return result