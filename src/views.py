import json
import logging
from datetime import datetime
from typing import Any, Dict
import pandas as pd
from src.utils import filter_by_date, read_excel

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

    return {"greeting": greeting, "period": f"{first_day} - {end_day}"}