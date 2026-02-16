from django.urls import path
from . import views

urlpatterns = [
    path('', views.checklist_list, name='checklist_list'),
    path('<int:pk>/', views.checklist_detail, name='checklist_detail'),
]
