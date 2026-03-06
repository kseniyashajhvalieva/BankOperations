import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def report_to_file(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для записи результата функции-отчёта в файл.

    Args:
        filename: Имя файла для записи. Если не указано,
                 генерируется автоматически.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Выполняем функцию
            result = func(*args, **kwargs)

            try:
                # Определяем имя файла
                if filename is None:
                    # Формируем имя: report_YYYYMMDD_HHMMSS.json
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"report_{timestamp}.json"
                else:
                    output_file = filename

                # Записываем результат
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"Отчёт сохранён в файл: {output_file}")

            except Exception as e:
                logger.error(f"Ошибка при сохранении отчёта: {e}")

            return result

        return wrapper

    return decorator


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Название категории
        date: Дата отсчёта (строка в формате 'DD.MM.YYYY').
              Если не указана, используется текущая дата.

    Returns:
        DataFrame с тратами по категории за последние 3 месяца
    """
    logger.info(f"Анализ трат по категории: {category}")

    # Определяем дату отсчёта
    if date is None:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(date, "%d.%m.%Y")

    # Начало периода (3 месяца назад)
    start_date = end_date - timedelta(days=90)

    # Фильтруем транзакции
    filtered = transactions[
        (transactions["Категория"] == category)
        & (transactions["Сумма операции"] < 0)  # только расходы
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ].copy()

    logger.info(f"Найдено {len(filtered)} транзакций по категории {category}")
    return filtered
