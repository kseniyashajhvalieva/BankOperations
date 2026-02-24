from src.services import simple_search


def test_simple_search_empty_query() -> None:
    """Поиск с пустым запросом возвращает пустой список."""
    transactions = [{"Описание": "тест", "Категория": "еда"}]
    result = simple_search("", transactions)
    assert result == []


def test_simple_search_empty_transactions() -> None:
    """Поиск по пустому списку возвращает пустой список."""
    result = simple_search("кофе", [])
    assert result == []


def test_simple_search_found_in_description() -> None:
    """Поиск находит транзакцию по описанию."""
    transactions = [
        {"Описание": "кофе в старбакс", "Категория": "кафе"},
        {"Описание": "молоко", "Категория": "супермаркеты"},
    ]
    result = simple_search("кофе", transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "кофе в старбакс"


def test_simple_search_found_in_category() -> None:
    """Поиск находит транзакцию по категории."""
    transactions = [{"Описание": "латте", "Категория": "кафе"}, {"Описание": "хлеб", "Категория": "супермаркеты"}]
    result = simple_search("кафе", transactions)
    assert len(result) == 1
    assert result[0]["Категория"] == "кафе"


def test_simple_search_case_insensitive() -> None:
    """Поиск не чувствителен к регистру."""
    transactions = [
        {"Описание": "Кофе в Старбакс", "Категория": "Кафе"},
        {"Описание": "Молоко", "Категория": "Супермаркеты"},
    ]
    result = simple_search("кофе", transactions)
    assert len(result) == 1
    assert result[0]["Описание"] == "Кофе в Старбакс"


def test_simple_search_multiple_results() -> None:
    """Поиск возвращает все подходящие транзакции."""
    transactions = [
        {"Описание": "кофе", "Категория": "кафе"},
        {"Описание": "кофемашина", "Категория": "техника"},
        {"Описание": "чай", "Категория": "продукты"},
    ]
    result = simple_search("кофе", transactions)
    assert len(result) == 2
