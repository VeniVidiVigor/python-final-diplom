from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact, CustomUser

# Регистрируем все созданные модели
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Shop)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductInfo)
admin.site.register(Parameter)
admin.site.register(ProductParameter)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Contact)
