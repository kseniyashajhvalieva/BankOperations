import pytest

from unittest.mock import mock_open, patch
import pandas as pd

from src.views import (
    get_greeting_by_hour,
    calculate_cards_data,
    get_top_transactions,
    load_user_settings,
    main_page
)


def test_get_greeting_by_hour():
    """Тест функции приветствия по времени."""
    assert get_greeting_by_hour(6) == "Доброе утро"
    assert get_greeting_by_hour(12) == "Добрый день"
    assert get_greeting_by_hour(18) == "Добрый вечер"
    assert get_greeting_by_hour(23) == "Доброй ночи"
    assert get_greeting_by_hour(3) == "Доброй ночи"


def test_calculate_cards_data():
    """Тест расчёта данных по картам."""
    # Создаём тестовый DataFrame
    data = {
        "Номер карты": ["*7197", "*7197", "*4556"],
        "Сумма операции": [-1000, -500, 1000],  # 2 расхода, 1 доход
    }
    df = pd.DataFrame(data)

    result = calculate_cards_data(df)

    # Должны быть только расходные карты
    assert len(result) == 1
    assert result[0]["last_digits"] == "7197"
    assert result[0]["total_spent"] == 1500
    assert result[0]["cashback"] == 15.0


def test_get_top_transactions():
    """Тест получения топ-5 транзакций."""
    data = {
        "Дата операции": ["01.01.2023", "02.01.2023", "03.01.2023"],
        "Сумма операции": [100, -500, 200],
        "Категория": ["Переводы", "Супермаркеты", "Аптеки"],
        "Описание": ["Перевод", "Магнит", "Аптека"],
    }
    df = pd.DataFrame(data)

    result = get_top_transactions(df, 3)

    assert len(result) == 3
    assert result[0]["Сумма операции"] == -500  # самая большая по модулю


@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD"], "user_stocks": ["AAPL"]}')
def test_load_user_settings_success(mock_file):
    """Тест успешной загрузки настроек."""
    settings = load_user_settings()
    assert settings["user_currencies"] == ["USD"]
    assert settings["user_stocks"] == ["AAPL"]


@patch("builtins.open", side_effect=FileNotFoundError)
def test_load_user_settings_not_found(mock_file):
    """Тест загрузки при отсутствии файла."""
    settings = load_user_settings()
    assert "USD" in settings["user_currencies"]
    assert "AAPL" in settings["user_stocks"]


@patch("src.views.read_excel")
@patch("src.views.filter_by_date")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.load_user_settings")
def test_main_page_success(
    mock_load_settings,
    mock_get_stocks,
    mock_get_currencies,
    mock_filter_date,
    mock_read_excel
):
    """Тест успешного выполнения main_page."""
    # Настройка моков
    mock_load_settings.return_value = {
        "user_currencies": ["USD"],
        "user_stocks": ["AAPL"]
    }

    # Создаём тестовый DataFrame
    data = {
        "Номер карты": ["*7197"],
        "Сумма операции": [-1000],
        "Дата операции": ["31.12.2023"],
        "Категория": ["Супермаркеты"],
        "Описание": ["Магнит"]
    }
    test_df = pd.DataFrame(data)

    mock_read_excel.return_value = test_df
    mock_filter_date.return_value = test_df
    mock_get_currencies.return_value = [{"currency": "USD", "rate": 90.0}]
    mock_get_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]

    # Вызов функции
    result = main_page("2024-01-15 10:30:00")

    # Проверки
    assert result["greeting"] == "Доброе утро"
    assert len(result["cards"]) == 1
    assert len(result["top_transactions"]) == 1
    assert len(result["currency_rates"]) == 1
    assert len(result["stock_prices"]) == 1
    assert "error" not in result