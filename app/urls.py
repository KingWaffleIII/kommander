from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path('', views.home, name='home'),
    path('edit/', views.edit, name='edit'),
    path('delete/', views.delete, name='delete'),
    path('terminal/', views.terminal, name='terminal'),
    
    path('login/', views.login, name='login'),
    path('two-factor/', views.two_factor_auth, name="2fa"),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('account/', views.account, name='account'),
    path('request-2fa/', views.request_2fa, name='2fa-request'),
    path('enable-2fa/', views.enable_2fa, name='2fa-enable'),
    path('disable-2fa/', views.disable_2fa, name='2fa-disable'),

    path('get-config/', views.get_config, name='get-config'),
]