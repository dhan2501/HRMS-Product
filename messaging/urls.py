# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.chat_home, name='chat_home'),
#     path('open/<int:user_id>/', views.open_chat, name='open_chat'),
#     path('room/<int:conv_id>/', views.chat_room, name='chat_room'),
#     path('room/<int:conv_id>/send/', views.send_message, name='send_message'),
#     path('room/<int:conv_id>/poll/', views.poll_messages, name='poll_messages'),
#     path('unread/', views.unread_count, name='unread_count'),
#     path('group/create/', views.create_group, name='create_group'),
# ]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('open/<int:user_id>/', views.open_chat, name='open_chat'),
    path('room/<int:conv_id>/', views.chat_room, name='chat_room'),
    path('room/<int:conv_id>/send/', views.send_message, name='send_message'),
    path('room/<int:conv_id>/poll/', views.poll_messages, name='poll_messages'),
    path('unread/', views.unread_count, name='unread_count'),
    path('list.json/', views.conv_list_json, name='conv_list_json'),
    path('group/create/', views.create_group, name='create_group'),
]