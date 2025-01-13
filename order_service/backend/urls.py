from django.urls import path
from django.http import JsonResponse
from backend.views import (
    ImportProductsAPIView,
    LoginAPIView,
    RegisterAPIView,
    ProductListAPIView,
    CartAPIView,
    ContactAPIView,
    ConfirmOrderAPIView,
    OrderHistoryAPIView,
)


def root_view(request):
    return JsonResponse({"message": "Welcome to the API. See the documentation for available endpoints."})


urlpatterns = [
    path('import-products/', ImportProductsAPIView.as_view(), name='import-products'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('contacts/', ContactAPIView.as_view(), name='contacts'),
    path('confirm-order/', ConfirmOrderAPIView.as_view(), name='confirm-order'),
    path('orders/', OrderHistoryAPIView.as_view(), name='order-history'),
]
