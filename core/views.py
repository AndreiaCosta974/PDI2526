from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from roteiros.models import Roteiro, Local, Dia
from django.conf import settings
import json


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


def _total_locais(r):
    return sum(len(d['locais']) for d in r['dias'])


ROTEIROS_EXEMPLO = [
    {
        'slug': 'lisboa-3-dias',
        'titulo': 'Lisboa em 3 Dias',
        'emoji': '🏛️',
        'descricao': 'Torre de Belém, Alfama, Pastéis de Belém e muito mais.',
        'destino': 'Lisboa, Portugal',
        'dias': [
            {
                'numero': 1, 'titulo': 'Belém e Descobrimentos',
                'locais': [
                    {'nome': 'Torre de Belém', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.6916, 'lng': -9.2160, 'notas': 'Símbolo de Lisboa, construída no séc. XVI.'},
                    {'nome': 'Mosteiro dos Jerónimos', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.6979, 'lng': -9.2067, 'notas': 'Património Mundial da UNESCO.'},
                    {'nome': 'Padrão dos Descobrimentos', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.6934, 'lng': -9.2063, 'notas': 'Monumento aos exploradores portugueses.'},
                    {'nome': 'Pastéis de Belém', 'tipo': 'restaurante', 'emoji': '🍽', 'lat': 38.6972, 'lng': -9.2059, 'notas': 'A pastelaria original desde 1837.'},
                ],
            },
            {
                'numero': 2, 'titulo': 'Alfama e Miradouros',
                'locais': [
                    {'nome': 'Castelo de São Jorge', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7139, 'lng': -9.1334, 'notas': 'Vista panorâmica sobre Lisboa.'},
                    {'nome': 'Miradouro da Graça', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7162, 'lng': -9.1286, 'notas': 'Um dos melhores miradouros da cidade.'},
                    {'nome': 'Museu do Fado', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7104, 'lng': -9.1298, 'notas': 'A história do fado português.'},
                ],
            },
            {
                'numero': 3, 'titulo': 'Baixa e LX Factory',
                'locais': [
                    {'nome': 'Praça do Comércio', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7075, 'lng': -9.1364, 'notas': 'A maior praça de Lisboa junto ao Tejo.'},
                    {'nome': 'LX Factory', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7027, 'lng': -9.1770, 'notas': 'Espaço criativo com lojas e restaurantes.'},
                ],
            },
        ],
    },
    {
        'slug': 'porto-classico',
        'titulo': 'Porto Clássico',
        'emoji': '🍷',
        'descricao': 'Ribeira, Livraria Lello, caves de vinho do Porto e Pont Luís I.',
        'destino': 'Porto, Portugal',
        'dias': [
            {
                'numero': 1, 'titulo': 'Ribeira e Caves',
                'locais': [
                    {'nome': 'Cais da Ribeira', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 41.1404, 'lng': -8.6137, 'notas': 'Zona histórica à beira do Douro.'},
                    {'nome': 'Ponte Luís I', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 41.1399, 'lng': -8.6096, 'notas': 'Icónica ponte metálica de dois tabuleiros.'},
                    {'nome': 'Caves Graham\'s', 'tipo': 'turismo', 'emoji': '🍷', 'lat': 41.1381, 'lng': -8.6139, 'notas': 'Visita e prova de vinho do Porto.'},
                ],
            },
            {
                'numero': 2, 'titulo': 'Centro Histórico',
                'locais': [
                    {'nome': 'Livraria Lello', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 41.1467, 'lng': -8.6153, 'notas': 'Uma das mais belas livrarias do mundo.'},
                    {'nome': 'Palácio da Bolsa', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 41.1412, 'lng': -8.6156, 'notas': 'Sala Árabe de beleza incomparável.'},
                    {'nome': 'Estação de São Bento', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 41.1454, 'lng': -8.6101, 'notas': 'Azulejos que contam a história de Portugal.'},
                    {'nome': 'Mercado do Bolhão', 'tipo': 'restaurante', 'emoji': '🍽', 'lat': 41.1490, 'lng': -8.6072, 'notas': 'Mercado histórico renovado com gastronomia local.'},
                ],
            },
        ],
    },
    {
        'slug': 'algarve-de-carro',
        'titulo': 'Algarve de Carro',
        'emoji': '🏖️',
        'descricao': 'Sagres, Praia da Marinha, Benagil e Tavira ao longo da costa.',
        'destino': 'Algarve, Portugal',
        'dias': [
            {
                'numero': 1, 'titulo': 'Sagres e Costa Vicentina',
                'locais': [
                    {'nome': 'Cabo de São Vicente', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 37.0247, 'lng': -8.9962, 'notas': 'O ponto mais a sudoeste da Europa.'},
                    {'nome': 'Fortaleza de Sagres', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 37.0107, 'lng': -8.9438, 'notas': 'Onde Henrique o Navegador planeou as grandes viagens.'},
                    {'nome': 'Praia do Martinhal', 'tipo': 'turismo', 'emoji': '🏖', 'lat': 37.0103, 'lng': -8.9259, 'notas': 'Praia calma ideal para famílias.'},
                ],
            },
            {
                'numero': 2, 'titulo': 'Costa Central — Benagil',
                'locais': [
                    {'nome': 'Praia da Marinha', 'tipo': 'turismo', 'emoji': '🏖', 'lat': 37.0830, 'lng': -8.4115, 'notas': 'Considerada uma das mais belas da Europa.'},
                    {'nome': 'Gruta de Benagil', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 37.0928, 'lng': -8.4278, 'notas': 'Caverna com abertura para o céu, acesso de barco.'},
                    {'nome': 'Praia de Carvoeiro', 'tipo': 'turismo', 'emoji': '🏖', 'lat': 37.0924, 'lng': -8.4690, 'notas': 'Vila piscatória com praia encaixada em falésia.'},
                ],
            },
            {
                'numero': 3, 'titulo': 'Tavira e Ria Formosa',
                'locais': [
                    {'nome': 'Centro Histórico de Tavira', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 37.1243, 'lng': -7.6499, 'notas': 'Uma das vilas mais autênticas do Algarve.'},
                    {'nome': 'Ria Formosa', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 37.0174, 'lng': -7.9314, 'notas': 'Parque Natural com lagoas e ilhas barreira.'},
                    {'nome': 'Ilha de Tavira', 'tipo': 'turismo', 'emoji': '🏖', 'lat': 37.1031, 'lng': -7.6410, 'notas': 'Acessível de barco, praia de areia fina.'},
                ],
            },
        ],
    },
    {
        'slug': 'sintra-magica',
        'titulo': 'Sintra Mágica',
        'emoji': '🏰',
        'descricao': 'Palácio Nacional, Quinta da Regaleira, Palácio da Pena e Cabo da Roca.',
        'destino': 'Sintra, Portugal',
        'dias': [
            {
                'numero': 1, 'titulo': 'Palácios e Mistérios',
                'locais': [
                    {'nome': 'Palácio Nacional de Sintra', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 38.7975, 'lng': -9.3869, 'notas': 'Residência medieval real no centro da vila.'},
                    {'nome': 'Quinta da Regaleira', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 38.7952, 'lng': -9.3939, 'notas': 'Jardins misteriosos com poços iniciáticos.'},
                    {'nome': 'Palácio da Pena', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 38.7879, 'lng': -9.3902, 'notas': 'Palácio romântico com cores vibrantes na Serra.'},
                    {'nome': 'Castelo dos Mouros', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 38.7929, 'lng': -9.3881, 'notas': 'Muralha medieval com vistas sobre a Serra.'},
                    {'nome': 'Cabo da Roca', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 38.7833, 'lng': -9.4997, 'notas': 'O ponto mais ocidental da Europa continental.'},
                ],
            },
        ],
    },
]


@login_required
def dashboard(request):
    roteiros = Roteiro.objects.filter(utilizador=request.user).order_by('-data_criacao')
    total_locais = Local.objects.filter(dia__roteiro__utilizador=request.user).count()
    total_dias = Dia.objects.filter(roteiro__utilizador=request.user).count()
    return render(request, 'dashboard.html', {
        'roteiros': roteiros,
        'total_locais': total_locais if total_locais > 0 else '—',
        'total_dias': total_dias if total_dias > 0 else '—',
        'roteiros_exemplo': [
            {**r, 'total_locais': _total_locais(r)} for r in ROTEIROS_EXEMPLO
        ],
    })


@login_required
def detalhe_exemplo(request, slug):
    roteiro = next((r for r in ROTEIROS_EXEMPLO if r['slug'] == slug), None)
    if roteiro is None:
        from django.http import Http404
        raise Http404
    total_locais = sum(len(d['locais']) for d in roteiro['dias'])
    locais_json = [
        {'nome': local['nome'], 'lat': local['lat'], 'lng': local['lng'], 'tipo': local['tipo'], 'dia': dia['numero']}
        for dia in roteiro['dias']
        for local in dia['locais']
    ]
    return render(request, 'detalhe_exemplo.html', {
        'roteiro': roteiro,
        'total_locais': total_locais,
        'locais_json': json.dumps(locais_json),
        'api_key': settings.GEOAPIFY_API_KEY,
    })


@login_required
def mapa(request):
    return render(request, 'mapa.html', {
        'api_key': settings.GEOAPIFY_API_KEY,
    })
