import json
import logging
from pprint import pprint

from src.utils import read_excel
from src.views import main_page
from src.services import simple_search
from src.reports import spending_by_category, report_to_file

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@report_to_file("category_report.json")
def demo_spending_by_category():
    """Демонстрация отчёта по категории."""
    df = read_excel("data/operations.xlsx")
    result = spending_by_category(df, "Супермаркеты", "31.12.2021")
    return result.to_dict(orient="records")


def main():
    """Главная функция для демонстрации всех возможностей."""
    print("=" * 50)
    print("ДЕМОНСТРАЦИЯ РАБОТЫ ПРИЛОЖЕНИЯ")
    print("=" * 50)

    # 1. Главная страница
    print("\n1. ГЛАВНАЯ СТРАНИЦА")
    print("-" * 30)
    result_main = main_page("2021-12-31 23:59:59")
    print("Приветствие:", result_main["greeting"])
    print("Карты:", json.dumps(result_main["cards"], indent=2, ensure_ascii=False))
    print("Топ-5 транзакций:", json.dumps(result_main["top_transactions"], indent=2, ensure_ascii=False))
    print("Курсы валют:", result_main["currency_rates"])
    print("Цены акций:", result_main["stock_prices"])

    # 2. Сервис поиска
    print("\n2. ПОИСК ТРАНЗАКЦИЙ")
    print("-" * 30)
    df = read_excel("data/operations.xlsx")
    transactions = df.to_dict(orient="records")
    search_result = simple_search("МТС", transactions)
    print(f"Найдено транзакций с 'МТС': {len(search_result)}")
    if search_result:
        print("Первая найденная:")
        pprint(search_result[0])

    # 3. Отчёт по категории
    print("\n3. ОТЧЁТ ПО КАТЕГОРИИ")
    print("-" * 30)
    report_data = demo_spending_by_category()
    print(f"Найдено транзакций по категории 'Супермаркеты': {len(report_data)}")
    if report_data:
        print("Первые 3 транзакции:")
        pprint(report_data[:3])
    print("\nОтчёт также сохранён в файл 'category_report.json'")

    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 50)


if __name__ == "__main__":
    main()