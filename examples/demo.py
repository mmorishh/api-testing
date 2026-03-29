"""
Иллюстративный пример работы API

Демонстрирует:
- Создание товара
- Получение товара по ID
- Обновление товара
- Удаление товара
- Получение списка товаров
- Загрузку нескольких товаров из JSON-файла

Запуск: python examples/demo.py
"""

import requests
import json
import time
from datetime import datetime

# Адреса API
FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5000"

# Цвета для вывода
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'


def print_section(title):
    """Печатает раздел с отступом"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_result(operation, status, data=None):
    """Печатает результат операции"""
    if status == "success":
        print(f"  {GREEN}✓{RESET} {operation}: OK")
        if data:
            print(f"    {data}")
    else:
        print(f"  {RED}✗{RESET} {operation}: FAILED")
        if data:
            print(f"    {data}")


def demo_fastapi():
    """Демонстрация работы FastAPI"""
    print_section("FASTAPI API ДЕМОНСТРАЦИЯ")
    
    try:
        # 1. Проверка здоровья
        print("\n1. Проверка здоровья API:")
        resp = requests.get(f"{FASTAPI_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            print(f"   {GREEN}✓{RESET} API работает: {resp.json()['framework']} v{resp.json()['version']}")
        else:
            print(f"   {RED}✗{RESET} API недоступен")
            return False
        
        # 2. Создание товара
        print("\n2. Создание товара:")
        new_item = {"name": "Тестовый товар", "price": 999.99}
        resp = requests.post(f"{FASTAPI_URL}/api/items/", json=new_item, timeout=10)
        
        if resp.status_code == 201:
            item = resp.json()
            item_id = item['id']
            print_result("Создание", "success", f"id={item_id}, name={item['name']}, price={item['price']}")
        else:
            print_result("Создание", "failed", resp.text)
            return False
        
        # 3. Получение товара по ID
        print(f"\n3. Получение товара (id={item_id}):")
        resp = requests.get(f"{FASTAPI_URL}/api/items/{item_id}", timeout=10)
        
        if resp.status_code == 200:
            item = resp.json()
            print_result("Получение", "success", f"name={item['name']}, price={item['price']}, in_stock={item['in_stock']}")
        else:
            print_result("Получение", "failed", resp.text)
            return False
        
        # 4. Обновление товара
        print(f"\n4. Обновление товара (id={item_id}):")
        update_data = {"price": 1499.99, "in_stock": False}
        resp = requests.put(f"{FASTAPI_URL}/api/items/{item_id}", json=update_data, timeout=10)
        
        if resp.status_code == 200:
            item = resp.json()
            print_result("Обновление", "success", f"новая цена={item['price']}, in_stock={item['in_stock']}")
        else:
            print_result("Обновление", "failed", resp.text)
            return False
        
        # 5. Получение списка товаров
        print("\n5. Получение списка товаров:")
        resp = requests.get(f"{FASTAPI_URL}/api/items/", timeout=10)
        
        if resp.status_code == 200:
            items = resp.json()
            print(f"   Всего товаров: {len(items)}")
            print(f"   Первые 3 товара:")
            for i, item in enumerate(items[:3]):
                print(f"     {i+1}. {item['name']} - {item['price']} руб.")
            print_result("Получение списка", "success")
        else:
            print_result("Получение списка", "failed", resp.text)
            return False
        
        # 6. Удаление товара
        print(f"\n6. Удаление товара (id={item_id}):")
        resp = requests.delete(f"{FASTAPI_URL}/api/items/{item_id}", timeout=10)
        
        if resp.status_code == 204:
            print_result("Удаление", "success", "товар удалён")
        else:
            print_result("Удаление", "failed", f"статус {resp.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}ОШИБКА:{RESET} Не удалось подключиться к FastAPI на {FASTAPI_URL}")
        print("Убедитесь, что контейнеры запущены: docker-compose up -d")
        return False
    except Exception as e:
        print(f"\n{RED}ОШИБКА:{RESET} {e}")
        return False


def demo_flask():
    """Демонстрация работы Flask"""
    print_section("FLASK API ДЕМОНСТРАЦИЯ")
    
    try:
        # 1. Проверка здоровья
        print("\n1. Проверка здоровья API:")
        resp = requests.get(f"{FLASK_URL}/api/health", timeout=5)
        if resp.status_code == 200:
            print(f"   {GREEN}✓{RESET} API работает: {resp.json()['framework']} v{resp.json()['version']}")
        else:
            print(f"   {RED}✗{RESET} API недоступен")
            return False
        
        # 2. Создание товара
        print("\n2. Создание товара:")
        new_item = {"name": "Тестовый товар", "price": 999.99}
        resp = requests.post(f"{FLASK_URL}/api/items/", json=new_item, timeout=10)
        
        if resp.status_code == 201:
            item = resp.json()
            item_id = item['id']
            print_result("Создание", "success", f"id={item_id}, name={item['name']}, price={item['price']}")
        else:
            print_result("Создание", "failed", resp.text)
            return False
        
        # 3. Получение товара по ID
        print(f"\n3. Получение товара (id={item_id}):")
        resp = requests.get(f"{FLASK_URL}/api/items/{item_id}", timeout=10)
        
        if resp.status_code == 200:
            item = resp.json()
            print_result("Получение", "success", f"name={item['name']}, price={item['price']}, in_stock={item['in_stock']}")
        else:
            print_result("Получение", "failed", resp.text)
            return False
        
        # 4. Обновление товара
        print(f"\n4. Обновление товара (id={item_id}):")
        update_data = {"price": 1499.99, "in_stock": False}
        resp = requests.put(f"{FLASK_URL}/api/items/{item_id}", json=update_data, timeout=10)
        
        if resp.status_code == 200:
            item = resp.json()
            print_result("Обновление", "success", f"новая цена={item['price']}, in_stock={item['in_stock']}")
        else:
            print_result("Обновление", "failed", resp.text)
            return False
        
        # 5. Получение списка товаров
        print("\n5. Получение списка товаров:")
        resp = requests.get(f"{FLASK_URL}/api/items/", timeout=10)
        
        if resp.status_code == 200:
            items = resp.json()
            print(f"   Всего товаров: {len(items)}")
            print(f"   Первые 3 товара:")
            for i, item in enumerate(items[:3]):
                print(f"     {i+1}. {item['name']} - {item['price']} руб.")
            print_result("Получение списка", "success")
        else:
            print_result("Получение списка", "failed", resp.text)
            return False
        
        # 6. Удаление товара
        print(f"\n6. Удаление товара (id={item_id}):")
        resp = requests.delete(f"{FLASK_URL}/api/items/{item_id}", timeout=10)
        
        if resp.status_code == 204:
            print_result("Удаление", "success", "товар удалён")
        else:
            print_result("Удаление", "failed", f"статус {resp.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n{RED}ОШИБКА:{RESET} Не удалось подключиться к Flask на {FLASK_URL}")
        print("Убедитесь, что контейнеры запущены: docker-compose up -d")
        return False
    except Exception as e:
        print(f"\n{RED}ОШИБКА:{RESET} {e}")
        return False


def load_sample_data():
    """Загрузка нескольких товаров из JSON-файла"""
    print_section("ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ ИЗ JSON")
    
    try:
        # Читаем JSON файл
        with open('examples/sample_data.json', 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        print(f"\nЗагружено {len(items)} товаров из sample_data.json")
        
        # Загружаем в FastAPI
        print("\nЗагрузка в FastAPI:")
        fastapi_ids = []
        for item in items:
            resp = requests.post(f"{FASTAPI_URL}/api/items/", json=item, timeout=10)
            if resp.status_code == 201:
                item_id = resp.json()['id']
                fastapi_ids.append(item_id)
                print(f"  ✓ {item['name']} -> id={item_id}")
            else:
                print(f"  ✗ {item['name']} - ошибка")
        
        # Загружаем в Flask
        print("\nЗагрузка в Flask:")
        flask_ids = []
        for item in items:
            resp = requests.post(f"{FLASK_URL}/api/items/", json=item, timeout=10)
            if resp.status_code == 201:
                item_id = resp.json()['id']
                flask_ids.append(item_id)
                print(f"  ✓ {item['name']} -> id={item_id}")
            else:
                print(f"  ✗ {item['name']} - ошибка")
        
        print(f"\n{GREEN}✓ Загружено {len(fastapi_ids)} товаров в FastAPI и {len(flask_ids)} в Flask{RESET}")
        return fastapi_ids, flask_ids
        
    except FileNotFoundError:
        print(f"\n{RED}ОШИБКА:{RESET} Файл examples/sample_data.json не найден")
        return [], []
    except Exception as e:
        print(f"\n{RED}ОШИБКА:{RESET} {e}")
        return [], []


def main():
    """Главная функция"""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}ИЛЛЮСТРАТИВНЫЙ ПРИМЕР РАБОТЫ API{RESET}")
    print(f"{YELLOW}Сравнение FastAPI и Flask{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"\nДата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Проверка доступности API
    print("\nПроверка доступности API...")
    
    # Демонстрация FastAPI
    fastapi_ok = demo_fastapi()
    
    # Демонстрация Flask
    flask_ok = demo_flask()
    
    # Загрузка тестовых данных
    if fastapi_ok and flask_ok:
        fastapi_ids, flask_ids = load_sample_data()
    
    # Итог
    print_section("ИТОГ")
    print(f"\nFastAPI: {'✓ Работает' if fastapi_ok else '✗ Недоступен'}")
    print(f"Flask:   {'✓ Работает' if flask_ok else '✗ Недоступен'}")
    
    if fastapi_ok and flask_ok:
        print(f"\n{GREEN}✓ Демонстрация завершена успешно{RESET}")
    else:
        print(f"\n{RED}✗ Демонстрация завершена с ошибками{RESET}")
        print("\nУбедитесь, что контейнеры запущены:")
        print("  docker-compose up -d")


if __name__ == "__main__":
    main()