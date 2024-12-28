from django.test import TestCase
from django.contrib.auth.models import User
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact


class ModelsTestCase(TestCase):

    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Создаем магазин
        self.shop = Shop.objects.create(name="Test Shop", url="http://test-shop.com")

        # Создаем категорию
        self.category = Category.objects.create(name="Test Category")
        self.category.shops.add(self.shop)

        # Создаем продукт
        self.product = Product.objects.create(name="Test Product", category=self.category)

        # Создаем информацию о продукте
        self.product_info = ProductInfo.objects.create(
            product=self.product,
            shop=self.shop,
            name="Test Product Info",
            quantity=10,
            price=100.00,
            price_rrc=120.00,
        )

        # Создаем параметр и привязываем его к продукту
        self.parameter = Parameter.objects.create(name="Color")
        self.product_parameter = ProductParameter.objects.create(
            product_info=self.product_info,
            parameter=self.parameter,
            value="Red"
        )

        # Создаем заказ
        self.order = Order.objects.create(user=self.user, status="new")

        # Создаем элемент в заказе
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            shop=self.shop,
            quantity=2
        )

        # Создаем контакт пользователя
        self.contact = Contact.objects.create(
            user=self.user,
            type="email",
            value="testuser@example.com"
        )

    def test_shop_creation(self):
        """Тест создания магазина"""
        self.assertEqual(self.shop.name, "Test Shop")
        self.assertEqual(self.shop.url, "http://test-shop.com")

    def test_category_relationship(self):
        """Тест связи категории и магазина"""
        self.assertIn(self.shop, self.category.shops.all())

    def test_product_relationship(self):
        """Тест связи продукта и категории"""
        self.assertEqual(self.product.category, self.category)

    def test_product_info_creation(self):
        """Тест информации о продукте"""
        self.assertEqual(self.product_info.product, self.product)
        self.assertEqual(self.product_info.shop, self.shop)
        self.assertEqual(self.product_info.name, "Test Product Info")
        self.assertEqual(self.product_info.quantity, 10)
        self.assertEqual(self.product_info.price, 100.00)
        self.assertEqual(self.product_info.price_rrc, 120.00)

    def test_product_parameter(self):
        """Тест параметра продукта"""
        self.assertEqual(self.product_parameter.product_info, self.product_info)
        self.assertEqual(self.product_parameter.parameter, self.parameter)
        self.assertEqual(self.product_parameter.value, "Red")

    def test_order_creation(self):
        """Тест создания заказа"""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.status, "new")
        self.assertIn(self.order_item, self.order.items.all())

    def test_contact_creation(self):
        """Тест создания контакта пользователя"""
        self.assertEqual(self.contact.user, self.user)
        self.assertEqual(self.contact.type, "email")
        self.assertEqual(self.contact.value, "testuser@example.com")