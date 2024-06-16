from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path
from . import views, forms

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('stat/', views.stat, name='stat'),
    path('class/', views.class_view, name='class'),
    path('', views.home, name='home'), 
]

urlpatterns += staticfiles_urlpatterns()
