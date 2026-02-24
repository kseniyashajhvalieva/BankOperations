import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime
import os

from src.utils import (
    read_excel,
    filter_by_date,
    get_currency_rates,
    get_stock_prices
)


def test_read_excel():
    """Тест чтения Excel-файла."""
    # Создаём тестовый файл
    test_data = {
        "Дата операции": ["31.12.2021 16:44:00"],
        "Сумма операции": [-160.89],
        "Категория": ["Супермаркеты"],
        "Описание": ["Колхоз"]
    }
    test_df = pd.DataFrame(test_data)
    test_df.to_excel("test_operations.xlsx", index=False)

    # Читаем файл
    result = read_excel("test_operations.xlsx")

    # Проверяем
    assert len(result) == 1
    assert result.iloc[0]["Сумма операции"] == -160.89
    assert "Дата операции" in result.columns

    # Удаляем тестовый файл
    os.remove("test_operations.xlsx")


def test_filter_by_date():
    """Тест фильтрации по дате."""
    # Создаём тестовый DataFrame
    data = {
        "Дата операции": [
            datetime(2021, 12, 1),
            datetime(2021, 12, 15),
            datetime(2021, 12, 31)
        ],
        "Сумма операции": [-100, -200, -300]
    }
    df = pd.DataFrame(data)

    # Фильтруем
    result = filter_by_date(df, "01.12.2021", "15.12.2021")

    # Проверяем
    assert len(result) == 2
    assert result.iloc[0]["Сумма операции"] == -100
    assert result.iloc[1]["Сумма операции"] == -200


@patch("requests.get")
def test_get_currency_rates(mock_get):
    """Тест получения курсов валют."""
    # Настройка мока
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "rates": {"USD": 90.5, "EUR": 99.8}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Вызов функции
    result = get_currency_rates(["USD", "EUR"])

    # Проверки
    assert len(result) == 2
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] > 0
    assert result[1]["currency"] == "EUR"
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_currency_rates_error(mock_get):
    """Тест обработки ошибки API валют."""
    mock_get.side_effect = Exception("API Error")

    result = get_currency_rates(["USD"])

    assert len(result) == 1
    assert result[0]["currency"] == "USD"
    assert result[0]["rate"] == 0


@patch("requests.get")
@patch.dict(os.environ, {"STOCK_API_KEY": "test_key"})
def test_get_stock_prices(mock_get):
    """Тест получения цен акций."""
    # Настройка мока
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Global Quote": {"05. price": "150.5"}
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 150.5


@patch("requests.get")
@patch.dict(os.environ, {"STOCK_API_KEY": "test_key"})
def test_get_stock_prices_error(mock_get):
    """Тест обработки ошибки API акций."""
    mock_get.side_effect = Exception("API Error")

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 0


@patch.dict(os.environ, {}, clear=True)
def test_get_stock_prices_no_key():
    """Тест без API-ключа."""
    result = get_stock_prices(["AAPL"])
    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 0