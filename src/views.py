import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def main_page(date_str: str) -> Dict[str, Any]:
    """Главная страница: возвращает JSON с данными за месяц."""
    # Загружаем настройки пользователя
    with open("user_settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)

    pass
    return {"message": "in development"}