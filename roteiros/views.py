from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Roteiro, Dia, Local
import json
from django.conf import settings
from django.http import JsonResponse

@login_required
def criar_roteiro(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descricao = request.POST.get('descricao', '')
        roteiro = Roteiro.objects.create(
            utilizador=request.user,
            titulo=titulo,
            descricao=descricao
        )
        messages.success(request, 'Roteiro criado!')
        return redirect('detalhe_roteiro', pk=roteiro.pk)
    return render(request, 'criar_roteiro.html')

@login_required
def detalhe_roteiro(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, utilizador=request.user)
    locais_json = []
    for dia in roteiro.dias.all():
        for local in dia.locais.all():
            locais_json.append({
                'nome': local.nome,
                'lat': local.latitude,
                'lng': local.longitude,
                'tipo': local.tipo,
                'dia': dia.numero,
            })
    return render(request, 'detalhe_roteiro.html', {
        'roteiro': roteiro,
        'locais_json': json.dumps(locais_json),
        'api_key': settings.GEOAPIFY_API_KEY,  # ← adiciona esta linha
    })
@login_required
def editar_roteiro(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, utilizador=request.user)
    if request.method == 'POST':
        roteiro.titulo = request.POST.get('titulo')
        roteiro.descricao = request.POST.get('descricao', '')
        roteiro.save()
        messages.success(request, 'Roteiro atualizado!')
        return redirect('detalhe_roteiro', pk=pk)
    return render(request, 'editar_roteiro.html', {'roteiro': roteiro})

@login_required
def eliminar_roteiro(request, pk):
    roteiro = get_object_or_404(Roteiro, pk=pk, utilizador=request.user)
    if request.method == 'POST':
        roteiro.delete()
        messages.success(request, 'Roteiro eliminado.')
        return redirect('dashboard')
    return render(request, 'confirmar_eliminar.html', {'roteiro': roteiro})

@login_required
def mapa(request):
    return render(request, 'mapa.html', {
        'api_key': settings.GEOAPIFY_API_KEY
    })

@login_required
def adicionar_dia(request, roteiro_pk):
    roteiro = get_object_or_404(Roteiro, pk=roteiro_pk, utilizador=request.user)
    if request.method == 'POST':
        numero = roteiro.dias.count() + 1
        titulo = request.POST.get('titulo', f'Dia {numero}')
        dia = Dia.objects.create(roteiro=roteiro, numero=numero, titulo=titulo)
        messages.success(request, f'Dia {numero} adicionado!')
    return redirect('detalhe_roteiro', pk=roteiro_pk)

@login_required
def adicionar_local(request, dia_pk):
    dia = get_object_or_404(Dia, pk=dia_pk, roteiro__utilizador=request.user)
    if request.method == 'POST':
        Local.objects.create(
            dia=dia,
            nome=request.POST.get('nome'),
            tipo=request.POST.get('tipo', 'turismo'),
            latitude=float(request.POST.get('latitude')),
            longitude=float(request.POST.get('longitude')),
            notas=request.POST.get('notas', ''),
            ordem=dia.locais.count() + 1
        )
        messages.success(request, 'Local adicionado!')
    return redirect('detalhe_roteiro', pk=dia.roteiro.pk)

@login_required  
def remover_local(request, local_pk):
    local = get_object_or_404(Local, pk=local_pk, dia__roteiro__utilizador=request.user)
    roteiro_pk = local.dia.roteiro.pk
    local.delete()
    messages.success(request, 'Local removido.')
    return redirect('detalhe_roteiro', pk=roteiro_pk)