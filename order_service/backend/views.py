from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, CustomUser, ProductInfo, Order, \
    Contact, OrderItem
from .serializers import ProductInfoSerializer, OrderItemSerializer, ContactSerializer
import yaml


class ImportProductsAPIView(APIView):
    """
    API для импорта товаров из YAML файла
    """

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'error': 'Authentication required'}, status=403)

        # Только пользователи с ролью shop могут загружать товары
        if not hasattr(request.user, 'type') or request.user.type != 'shop':
            return JsonResponse({'status': False, 'error': 'Only shops can upload products'}, status=403)

        # Получаем файл из запроса
        yaml_file = request.FILES.get('file')
        if not yaml_file:
            return JsonResponse({'status': False, 'error': 'YAML file is required'}, status=400)

        # Загрузка и парсинг YAML файла
        try:
            data = yaml.safe_load(yaml_file)
        except yaml.YAMLError as e:
            return JsonResponse({'status': False, 'error': f'YAML parsing error: {e}'}, status=400)

        # Импортируем данные в базу
        try:
            shop, _ = Shop.objects.get_or_create(name=data['shop'])

            # Импортируем категории
            for category in data['categories']:
                category_object, _ = Category.objects.get_or_create(
                    id=category['id'],
                    defaults={'name': category['name']}
                )
                category_object.shops.add(shop)
                category_object.save()

            # Удаляем текущие товары магазина
            ProductInfo.objects.filter(shop=shop).delete()

            # Импортируем товары
            for item in data['goods']:
                product, _ = Product.objects.get_or_create(
                    name=item['name'],
                    category_id=item['category']
                )

                product_info = ProductInfo.objects.create(
                    product=product,
                    shop=shop,
                    external_id=item['id'],
                    model=item['model'],
                    price=item['price'],
                    price_rrc=item['price_rrc'],
                    quantity=item['quantity']
                )

                # Импортируем параметры товара
                for name, value in item['parameters'].items():
                    parameter_object, _ = Parameter.objects.get_or_create(name=name)
                    ProductParameter.objects.create(
                        product_info=product_info,
                        parameter=parameter_object,
                        value=value
                    )

            return JsonResponse({'status': True, 'message': 'Products imported successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'status': False, 'error': f'Error during import: {e}'}, status=500)


class LoginAPIView(APIView):
    """
    API View для входа пользователя (авторизация)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email и пароль обязательны'}, status=400)

        user = authenticate(username=email, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=200)

        return Response({'error': 'Неверные учетные данные'}, status=400)


class RegisterAPIView(APIView):
    """
    API View для регистрации пользователя
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')

        if not email or not password or not first_name or not last_name:
            return Response({'error': 'Все поля обязательны'}, status=400)

        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Пользователь с таким email уже существует'}, status=400)

        user = CustomUser.objects.create_user(
            username=email,  # Используем email как username.
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )

        return Response({'message': 'Пользователь успешно зарегистрирован'}, status=201)


class ProductListAPIView(ListAPIView):
    """
    API для получения списка товаров
    """
    queryset = ProductInfo.objects.all()
    serializer_class = ProductInfoSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'product__category__name']  # Фильтрация по названию и категории


class CartAPIView(APIView):
    """
    API для работы с корзиной пользователя
    """

    def get(self, request):
        cart = Order.objects.filter(user=request.user, status='new').first()
        if not cart:
            return Response({'message': 'Корзина пуста'}, status=200)

        items = cart.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity')

        if not product_id or not quantity:
            return Response({'error': 'Необходимо указать product_id и quantity'}, status=400)

        try:
            # Получаем или создаём новую корзину
            cart, _ = Order.objects.get_or_create(user=request.user, status='new')

            # Получаем продукт
            product = Product.objects.get(id=product_id)

            # Получаем магазин, связанный с продуктом
            product_info = ProductInfo.objects.filter(product=product).first()
            if not product_info:
                return Response({'error': 'Информация о продукте не найдена'}, status=404)

            shop = product_info.shop

            # Создаём или обновляем товар в корзине
            order_item, created = OrderItem.objects.get_or_create(
                order=cart,
                product=product,
                shop=shop,  # Устанавливаем значение для обязательного поля shop
                defaults={'quantity': quantity}
            )

            # Обновляем количество, если товар уже существует в корзине
            if not created:
                order_item.quantity = quantity
                order_item.save()

            return Response({'message': 'Товар добавлен в корзину'}, status=201)
        except Product.DoesNotExist:
            return Response({'error': 'Указанный продукт не найден'}, status=404)

    def delete(self, request):
        item_id = request.data.get('item_id')
        OrderItem.objects.filter(id=item_id).delete()
        return Response({'message': 'Удалено из корзины'}, status=204)


class ContactAPIView(APIView):
    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        contact = Contact.objects.create(
            user=request.user, type=data.get('type'), value=data.get('value')
        )
        return Response({'message': 'Контакт добавлен', 'id': contact.id}, status=201)

    def delete(self, request):
        contact_id = request.data.get('id')
        Contact.objects.filter(user=request.user, id=contact_id).delete()
        return Response({'message': 'Контакт удален'}, status=204)


class ConfirmOrderAPIView(APIView):
    """
    API для подтверждения заказа пользователя
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        contact_id = request.data.get('contact_id')

        if not order_id or not contact_id:
            return Response({'error': 'ID заказа и ID контакта обязательны'}, status=400)

        # Проверим существование заказа
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({'error': 'Заказ не найден'}, status=404)

        # Проверим существование контакта
        contact = Contact.objects.filter(id=contact_id, user=request.user).first()
        if not contact:
            return Response({'error': 'Контакт не найден'}, status=404)

        # Обновляем статус заказа
        order.status = 'in_progress'  # Или другой нужный статус
        order.contact = contact
        order.save()

        return Response({'message': 'Заказ успешно подтвержден', 'order_id': order.id}, status=200)


class OrderHistoryAPIView(APIView):
    """
    API для просмотра истории заказов пользователя
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).exclude(status='new')  # Исключаем "новые" заказы
        data = []
        for order in orders:
            total_price = sum(
                item.quantity * item.product.price
                for item in order.items.all()
            )
            data.append({
                'id': order.id,
                'date': order.dt,
                'status': order.status,
                'total_price': total_price,
            })

        return Response(data, status=200)