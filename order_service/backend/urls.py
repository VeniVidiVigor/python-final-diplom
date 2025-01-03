from django.urls import path
from backend.views import ImportProductsAPIView

urlpatterns = [
    path('import-products/', ImportProductsAPIView.as_view(), name='import-products'),
]
