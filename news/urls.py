from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('saved/', views.saved_articles, name='saved_articles'),
    path('save/<int:news_id>/', views.toggle_save, name='toggle_save'),
    path('register/', views.register, name='register'),
]
