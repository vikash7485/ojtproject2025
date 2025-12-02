from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # For built-in auth views if needed, but we'll make custom ones or map them
]
