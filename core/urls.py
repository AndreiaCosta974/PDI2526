from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('perfil/', views.perfil, name='perfil'),
    path('explorar/', views.explorar, name='explorar'),
    path('roteiro-publico/<int:pk>/', views.roteiro_publico, name='roteiro_publico'),
    path('mapa/', views.mapa, name='mapa'),
    path('exemplo/<slug:slug>/', views.detalhe_exemplo, name='detalhe_exemplo'),
    path('exemplo/<slug:slug>/copiar/', views.copiar_exemplo, name='copiar_exemplo'),
]