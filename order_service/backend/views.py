from django.http import JsonResponse
from rest_framework.views import APIView
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
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
