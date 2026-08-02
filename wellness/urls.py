from django.urls import path
from . import views

urlpatterns = [
    path('', views.wellness_list, name='wellness_list'),
    path('add/', views.add_wellness, name='add_wellness'),
    path('<int:pk>/edit/', views.edit_wellness, name='edit_wellness'),
    path('<int:pk>/delete/', views.delete_wellness, name='delete_wellness'),
]