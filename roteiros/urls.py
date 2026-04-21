from django.urls import path
from . import views

urlpatterns = [
    path('roteiro/novo/', views.criar_roteiro, name='criar_roteiro'),
    path('roteiro/<int:pk>/', views.detalhe_roteiro, name='detalhe_roteiro'),
    path('roteiro/<int:pk>/editar/', views.editar_roteiro, name='editar_roteiro'),
    path('roteiro/<int:pk>/eliminar/', views.eliminar_roteiro, name='eliminar_roteiro'),
    path('roteiro/<int:roteiro_pk>/adicionar-dia/', views.adicionar_dia, name='adicionar_dia'),
    path('dia/<int:dia_pk>/adicionar-local/', views.adicionar_local, name='adicionar_local'),
    path('local/<int:local_pk>/remover/', views.remover_local, name='remover_local'),
    path('guardar-rota-mapa/', views.guardar_rota_mapa, name='guardar_rota_mapa'),
]
