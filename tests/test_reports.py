from datetime import datetime
from unittest.mock import mock_open, patch

import pandas as pd

from src.reports import report_to_file, spending_by_category


def test_spending_by_category_empty() -> None:
    """Тест с пустым DataFrame."""
    df = pd.DataFrame(columns=["Категория", "Сумма операции", "Дата операции"])
    result = spending_by_category(df, "Супермаркеты", "15.01.2024")
    assert len(result) == 0


def test_spending_by_category_filter() -> None:
    """Тест фильтрации по категории и дате."""
    # Создаём тестовые данные
    data = {
        "Категория": ["Супермаркеты", "Супермаркеты", "Аптеки", "Супермаркеты"],
        "Сумма операции": [-1000, -500, -300, 200],  # 200 - доход, не должен попасть
        "Дата операции": [datetime(2024, 1, 10), datetime(2024, 2, 15), datetime(2024, 1, 20), datetime(2024, 1, 25)],
    }
    df = pd.DataFrame(data)

    # Дата отсчёта - 15.03.2024, период 90 дней назад = 15.12.2023
    result = spending_by_category(df, "Супермаркеты", "15.03.2024")

    # Должны попасть: первые две (супермаркеты, расходы, в периоде)
    # Третья - другая категория
    # Четвёртая - супермаркеты, но доход
    assert len(result) == 2
    assert result.iloc[0]["Сумма операции"] == -1000
    assert result.iloc[1]["Сумма операции"] == -500


def test_spending_by_category_no_date() -> None:
    """Тест с датой по умолчанию (текущая)."""
    # Патчим datetime.now() для предсказуемости
    with patch("src.reports.datetime") as mock_datetime:
        mock_datetime.now.return_value = datetime(2024, 3, 15)
        mock_datetime.strptime = datetime.strptime

        data = {
            "Категория": ["Супермаркеты"],
            "Сумма операции": [-1000],
            "Дата операции": [datetime(2024, 1, 10)],  # в периоде
        }
        df = pd.DataFrame(data)

        result = spending_by_category(df, "Супермаркеты")
        assert len(result) == 1


@patch("builtins.open", new_callable=mock_open)
def test_report_to_file_decorator(mock_file) -> None:
    """Тест декоратора report_to_file."""

    @report_to_file("test_report.json")
    def test_func():
        return {"test": "data"}

    result = test_func()

    assert result == {"test": "data"}
    mock_file.assert_called_once_with("test_report.json", "w", encoding="utf-8")
    mock_file().write.assert_called()


def test_report_to_file_default_name() -> None:
    """Тест декоратора с именем файла по умолчанию."""
    with patch("builtins.open", new_callable=mock_open) as mock_file:
        with patch("src.reports.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 3, 15, 12, 30, 45)
            mock_datetime.strftime = datetime.strftime

            @report_to_file()
            def test_func():
                return {"key": "value"}

            result = test_func()

            assert result == {"key": "value"}
            # Проверяем, что имя файла сформировано правильно
            expected_name = "report_20240315_123045.json"
            mock_file.assert_called_once_with(expected_name, "w", encoding="utf-8")
