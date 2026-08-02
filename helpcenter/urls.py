from django.urls import path
from . import views

urlpatterns = [
    path('', views.help_home, name='help_home'),
    path('manage/', views.manage_policies, name='manage_policies'),
    path('manage/category/add/', views.add_category, name='add_category'),
    path('manage/category/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('manage/category/<int:category_id>/document/add/', views.add_document, name='add_document'),
    path('manage/document/<int:pk>/delete/', views.delete_document, name='delete_document'),
]