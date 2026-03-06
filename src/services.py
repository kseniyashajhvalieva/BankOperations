import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ищет транзакции по строке в описании или категории.

    Args:
        query: Строка для поиска
        transactions: Список транзакций (словарей)

    Returns:
        Список транзакций, содержащих query в описании или категории
    """
    logger.info(f"Поиск по запросу: '{query}'")

    if not query or not transactions:
        return []

    query_lower = query.lower()
    result = []

    for transaction in transactions:
        description = transaction.get("Описание", "").lower()
        category = transaction.get("Категория", "").lower()

        if query_lower in description or query_lower in category:
            result.append(transaction)

    logger.info(f"Найдено {len(result)} транзакций")
    return result
