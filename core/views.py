from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from roteiros.models import Roteiro, Local, Dia
from django.conf import settings


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conta criada com sucesso! Faz login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):
    roteiros = Roteiro.objects.filter(utilizador=request.user).order_by('-data_criacao')
    total_locais = Local.objects.filter(dia__roteiro__utilizador=request.user).count()
    total_dias = Dia.objects.filter(roteiro__utilizador=request.user).count()
    return render(request, 'dashboard.html', {
        'roteiros': roteiros,
        'total_locais': total_locais if total_locais > 0 else '—',
        'total_dias': total_dias if total_dias > 0 else '—',
    })


@login_required
def mapa(request):
    return render(request, 'mapa.html', {
        'api_key': settings.GEOAPIFY_API_KEY,
    })
