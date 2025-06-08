
from django.urls import path
from .views import dashboard, bin_list, bin_detail

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('bins/', bin_list, name='bin_list'),
    path('bins/<str:bin_id>/', bin_detail, name='bin_detail'),
]
