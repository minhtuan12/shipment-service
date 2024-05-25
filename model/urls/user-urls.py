from django.urls import path
from model import views

urlpatterns = [
    path('', views.my_shipments),
    path('create', views.create_shipment),
]
