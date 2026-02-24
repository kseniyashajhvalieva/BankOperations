import json
import logging
from datetime import datetime
from functools import wraps
from typing import Callable, Optional, Any

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
        def wrapper(*args, **kwargs) -> Any:
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