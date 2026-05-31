import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


class Topping:
    def __init__(self, name: str, price: float):
        self.name = name
        self.price = price


class Pizza(ABC):
    def __init__(self, name: str, base_price: float):
        self.name = name
        self.base_price = base_price
        self.toppings: List[Topping] = []

    @abstractmethod
    def get_description(self) -> str:
        pass

    def get_total_price(self) -> float:
        return self.base_price + sum(t.price for t in self.toppings)

    def add_topping(self, topping: Topping):
        self.toppings.append(topping)


class Margherita(Pizza):
    def __init__(self):
        super().__init__("Маргарита", 350.0)

    def get_description(self) -> str:
        return "Томатный соус, моцарелла, базилик"


class Pepperoni(Pizza):
    def __init__(self):
        super().__init__("Пепперони", 420.0)

    def get_description(self) -> str:
        return "Томатный соус, моцарелла, пепперони"


class Hawaiian(Pizza):
    def __init__(self):
        super().__init__("Гавайская", 400.0)

    def get_description(self) -> str:
        return "Томатный соус, моцарелла, ветчина, ананасы"


class FourCheese(Pizza):
    def __init__(self):
        super().__init__("Четыре сыра", 480.0)

    def get_description(self) -> str:
        return "Моцарелла, пармезан, горгонзола, рикотта"


class CustomPizza(Pizza):
    def __init__(self, name: str, base_price: float):
        super().__init__(name, base_price)

    def get_description(self) -> str:
        return "Свой рецепт"


class Order:
    def __init__(self, order_id: int):
        self.id = order_id
        self.pizzas: List[Pizza] = []
        self.created_at = datetime.now()

    def add_pizza(self, pizza: Pizza):
        self.pizzas.append(pizza)

    def get_total(self) -> float:
        return sum(p.get_total_price() for p in self.pizzas)

    def get_profit(self) -> float:
        return sum(p.get_total_price() - p.base_price for p in self.pizzas)



class OrderRepository:
    def __init__(self):
        self.file = "orders.json"
        if not os.path.exists(self.file):
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save(self, order: Order):
        with open(self.file, "r", encoding="utf-8") as f:
            orders = json.load(f)
        orders.append({
            "id": order.id,
            "pizzas": [
                {
                    "name": p.name,
                    "toppings": [t.name for t in p.toppings],
                    "price": p.get_total_price()
                }
                for p in order.pizzas
            ],
            "total": order.get_total(),
            "profit": order.get_profit(),
            "time": order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        })
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(orders, f, ensure_ascii=False, indent=2)

    def get_all(self) -> list:
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)



class MenuRepository:
    def __init__(self):
        self.file = "menu.json"
        if not os.path.exists(self.file):
            default = {
                "pizzas": [
                    {"type": "Margherita", "name": "Маргарита", "price": 350.0},
                    {"type": "Pepperoni", "name": "Пепперони", "price": 420.0},
                    {"type": "Hawaiian", "name": "Гавайская", "price": 400.0},
                    {"type": "FourCheese", "name": "Четыре сыра", "price": 480.0}
                ],
                "toppings": [
                    {"name": "Сыр", "price": 50.0},
                    {"name": "Ветчина", "price": 70.0},
                    {"name": "Грибы", "price": 45.0}
                ]
            }
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)

    def load(self) -> dict:
        with open(self.file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)



class OrderService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.repo = OrderRepository()
            orders = cls._instance.repo.get_all()
            cls._instance.next_id = max([o["id"] for o in orders], default=0) + 1
        return cls._instance

    def create_order(self) -> Order:
        order = Order(self.next_id)
        self.next_id += 1
        return order

    def complete_order(self, order: Order):
        self.repo.save(order)


class MenuService:
    def __init__(self):
        self.repo = MenuRepository()

    def get_pizzas(self) -> List[Pizza]:
        data = self.repo.load()
        mapping = {
            "Margherita": Margherita,
            "Pepperoni": Pepperoni,
            "Hawaiian": Hawaiian,
            "FourCheese": FourCheese
        }
        pizzas = []
        for p in data["pizzas"]:
            if p["type"] in mapping:
                pizza = mapping[p["type"]]()
                pizza.base_price = p["price"]
                pizzas.append(pizza)
        return pizzas

    def get_toppings(self) -> List[Topping]:
        return [Topping(t["name"], t["price"]) for t in self.repo.load()["toppings"]]

    def add_pizza(self, type_name: str, name: str, price: float):
        data = self.repo.load()
        data["pizzas"].append({"type": type_name, "name": name, "price": price})
        self.repo.save(data)

    def remove_pizza(self, name: str):
        data = self.repo.load()
        data["pizzas"] = [p for p in data["pizzas"] if p["name"] != name]
        self.repo.save(data)

    def add_topping(self, name: str, price: float):
        data = self.repo.load()
        data["toppings"].append({"name": name, "price": price})
        self.repo.save(data)

    def remove_topping(self, name: str):
        data = self.repo.load()
        data["toppings"] = [t for t in data["toppings"] if t["name"] != name]
        self.repo.save(data)



class ReportService:
    def __init__(self):
        self.repo = OrderRepository()

    def get_report(self) -> dict:
        orders = self.repo.get_all()
        pizza_count = {}
        total_revenue = 0
        total_profit = 0
        for o in orders:
            total_revenue += o["total"]
            total_profit += o["profit"]
            for p in o["pizzas"]:
                pizza_count[p["name"]] = pizza_count.get(p["name"], 0) + 1
        return {
            "orders": len(orders),
            "revenue": total_revenue,
            "profit": total_profit,
            "pizzas": pizza_count
        }



class App:
    def __init__(self):
        self.menu = MenuService()
        self.orders = OrderService()
        self.report = ReportService()

    def run(self):
        while True:
            print("\n1. Сделать заказ")
            print("2. Отчеты")
            print("3. Админ-панель")
            print("4. Выход")
            c = input("> ")
            if c == "1":
                self.make_order()
            elif c == "2":
                self.show_report()
            elif c == "3":
                self.admin()
            elif c == "4":
                break

    def make_order(self):
        order = self.orders.create_order()
        while True:
            print("\n1. Стандартная пицца")
            print("2. Свой рецепт")
            print("3. Завершить")
            c = input("> ")
            if c == "1":
                pizza = self.select_pizza()
                if pizza:
                    self.add_toppings(pizza)
                    order.add_pizza(pizza)
            elif c == "2":
                name = input("Название: ")
                try:
                    price = float(input("Цена: "))
                except ValueError:
                    print("Неверная цена")
                    continue
                pizza = CustomPizza(name, price)
                self.add_toppings(pizza)
                order.add_pizza(pizza)
            elif c == "3":
                if order.pizzas:
                    self.orders.complete_order(order)
                    print(f"\nЗаказ #{order.id}")
                    for p in order.pizzas:
                        print(f"  {p.name} - {p.get_total_price()} руб.")
                    print(f"Итого: {order.get_total()} руб.")
                break

    def select_pizza(self):
        pizzas = self.menu.get_pizzas()
        for i, p in enumerate(pizzas, 1):
            print(f"{i}. {p.name} - {p.base_price} руб.")
        try:
            n = int(input("Номер: "))
            return pizzas[n - 1] if 1 <= n <= len(pizzas) else None
        except (ValueError, IndexError):
            return None

    def add_toppings(self, pizza: Pizza):
        toppings = self.menu.get_toppings()
        while True:
            print("\nТоппинги:")
            for i, t in enumerate(toppings, 1):
                print(f"{i}. {t.name} (+{t.price} руб.)")
            print("0. Готово")
            try:
                n = int(input("> "))
                if n == 0:
                    break
                if 1 <= n <= len(toppings):
                    pizza.add_topping(toppings[n - 1])
            except ValueError:
                pass

    def show_report(self):
        r = self.report.get_report()
        print(f"\nЗаказов: {r['orders']}")
        print(f"Выручка: {r['revenue']} руб.")
        print(f"Прибыль: {r['profit']} руб.")
        print("Продажи:")
        for name, count in r["pizzas"].items():
            print(f"  {name}: {count} шт.")

    def admin(self):
        while True:
            print("\n1. Показать меню")
            print("2. Добавить пиццу")
            print("3. Удалить пиццу")
            print("4. Добавить топпинг")
            print("5. Удалить топпинг")
            print("6. Назад")
            c = input("> ")
            if c == "1":
                for p in self.menu.get_pizzas():
                    print(f"  {p.name} - {p.base_price} руб.")
                for t in self.menu.get_toppings():
                    print(f"  {t.name} (+{t.price} руб.)")
            elif c == "2":
                name = input("Название: ")
                try:
                    price = float(input("Цена: "))
                except ValueError:
                    continue
                self.menu.add_pizza("CustomPizza", name, price)
            elif c == "3":
                pizzas = self.menu.get_pizzas()
                for i, p in enumerate(pizzas, 1):
                    print(f"{i}. {p.name}")
                try:
                    n = int(input("Номер: "))
                    if 1 <= n <= len(pizzas):
                        self.menu.remove_pizza(pizzas[n - 1].name)
                except ValueError:
                    pass
            elif c == "4":
                name = input("Название: ")
                try:
                    price = float(input("Цена: "))
                except ValueError:
                    continue
                self.menu.add_topping(name, price)
            elif c == "5":
                toppings = self.menu.get_toppings()
                for i, t in enumerate(toppings, 1):
                    print(f"{i}. {t.name}")
                try:
                    n = int(input("Номер: "))
                    if 1 <= n <= len(toppings):
                        self.menu.remove_topping(toppings[n - 1].name)
                except ValueError:
                    pass
            elif c == "6":
                break


if __name__ == "__main__":
    App().run()


#Singleton - чтобы счетчик id заказов был один на всю программу и не сбрасывался

#Factory Method - Каждая пицца сама знает цену и описание новый тип добавляется новым классом

#Repository - вынес работу с json в отдельные классы, чтобы сервисы не лазили в файлы напрямую