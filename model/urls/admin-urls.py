from django.urls import path
from model import views

urlpatterns = [
    path('', views.get_all_shipments),
    path('<int:id>/update-status', views.update_status),
]
