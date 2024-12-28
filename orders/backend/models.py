from django.db import models
from django.contrib.auth.models import User


# Create your models here.

# Модель магазина
class Shop(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название магазина")
    url = models.URLField(verbose_name="Ссылка на магазин")

    def __str__(self):
        return self.name


# Модель категории
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")
    shops = models.ManyToManyField(Shop, related_name="categories", verbose_name="Магазины категории")

    def __str__(self):
        return self.name


# Модель продукта
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    name = models.CharField(max_length=255, verbose_name="Название продукта")

    def __str__(self):
        return self.name


# Модель дополнительной информации о продукте
class ProductInfo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_infos", verbose_name="Продукт")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="product_infos", verbose_name="Магазин")
    name = models.CharField(max_length=255, verbose_name="Название информации")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    price_rrc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Рекомендуемая цена")

    def __str__(self):
        return f"{self.product.name} ({self.shop.name})"


# Модель параметров для продукта
class Parameter(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название параметра")

    def __str__(self):
        return self.name


# Модель значений параметров продукта
class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name="parameters",
                                     verbose_name="Продуктовая информация")
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name="product_parameters",
                                  verbose_name="Параметр")
    value = models.CharField(max_length=255, verbose_name="Значение параметра")

    def __str__(self):
        return f"{self.parameter.name}: {self.value}"


# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("in_progress", "В процессе"),
        ("completed", "Завершён"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь")
    dt = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус заказа")

    def __str__(self):
        return f"Order {self.id} ({self.get_status_display()})"


# Модель элемента заказа
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items", verbose_name="Продукт")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="order_items", verbose_name="Магазин")
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# Модель для контактов
class Contact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Телефон"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="contacts", verbose_name="Пользователь")
    type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, verbose_name="Тип контакта")
    value = models.CharField(max_length=255, verbose_name="Значение")

    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"
