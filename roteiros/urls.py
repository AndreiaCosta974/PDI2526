from django.urls import path
from . import views

urlpatterns = [
    path('roteiro/novo/', views.criar_roteiro, name='criar_roteiro'),
    path('roteiro/<int:pk>/', views.detalhe_roteiro, name='detalhe_roteiro'),
    path('roteiro/<int:pk>/editar/', views.editar_roteiro, name='editar_roteiro'),
    path('roteiro/<int:pk>/eliminar/', views.eliminar_roteiro, name='eliminar_roteiro'),
    path('roteiro/<int:roteiro_pk>/adicionar-dia/', views.adicionar_dia, name='adicionar_dia'),
    path('dia/<int:dia_pk>/editar/', views.editar_dia, name='editar_dia'),
    path('dia/<int:dia_pk>/eliminar/', views.eliminar_dia, name='eliminar_dia'),
    path('dia/<int:dia_pk>/mover/<str:direcao>/', views.mover_dia, name='mover_dia'),
    path('dia/<int:dia_pk>/adicionar-local/', views.adicionar_local, name='adicionar_local'),
    path('local/<int:local_pk>/editar/', views.editar_local, name='editar_local'),
    path('local/<int:local_pk>/mover/<str:direcao>/', views.mover_local, name='mover_local'),
    path('local/<int:local_pk>/remover/', views.remover_local, name='remover_local'),
    path('guardar-rota-mapa/', views.guardar_rota_mapa, name='guardar_rota_mapa'),
]
