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
        'slug': 'bangkok-thailand',
        'titulo': 'Bangkok em 4 Dias',
        'emoji': '🏛️',
        'descricao': 'Grand Palace, Templos milenares, mercados vibrantes e vida noturna agitada.',
        'destino': 'Bangkok, Tailândia',
        'dias': [
            {
                'numero': 1, 'titulo': 'Coração Histórico e Templos',
                'locais': [
                    {'nome': 'Grand Palace', 'tipo': 'turismo', 'emoji': '🏯', 'lat': 13.7500, 'lng': 100.4913, 'notas': 'Palácio histórico com arquitetura tradicional.'},
                    {'nome': 'Wat Phra Kaew', 'tipo': 'turismo', 'emoji': '⛩️', 'lat': 13.7516, 'lng': 100.4927, 'notas': 'Templo sagrado com ouro e jade.'},
                    {'nome': 'Wat Pho', 'tipo': 'turismo', 'emoji': '🗿', 'lat': 13.7465, 'lng': 100.4933, 'notas': 'Templo budista com grandes esculturas.'},
                ],
            },
            {
                'numero': 2, 'titulo': 'Rio e Mochileiros',
                'locais': [
                    {'nome': 'Wat Arun', 'tipo': 'turismo', 'emoji': '🛕', 'lat': 13.7437, 'lng': 100.4889, 'notas': 'Templo budista com vistas panorâmicas.'},
                    {'nome': 'Bubble in the Forest Cafe', 'tipo': 'restaurante', 'emoji': '☕', 'lat': 13.7925, 'lng': 100.3325, 'notas': 'Café único dentro de uma bolha transparente.'},
                    {'nome': 'Khao San Road', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': 13.7590, 'lng': 100.4971, 'notas': 'Rua famosa entre mochileiros com muitos bares e restaurantes.'},
                ],
            },
            {
                'numero': 3, 'titulo': 'Mercados e Rooftops',
                'locais': [
                    {'nome': 'Mercado Chatuchak', 'tipo': 'compras', 'emoji': '🛍️', 'lat': 13.8000, 'lng': 100.5500, 'notas': 'O maior mercado de Bangkok.'},
                    {'nome': 'Tichuca Rooftop Bar', 'tipo': 'nightlife', 'emoji': '🍹', 'lat': 13.7228, 'lng': 100.5810, 'notas': 'Bar rooftop com vista panorâmica.'},
                    {'nome': 'Sukhumvit Soi 11', 'tipo': 'nightlife', 'emoji': '🪩', 'lat': 13.7443, 'lng': 100.5554, 'notas': 'Rua animada com muitos bares e clubes.'},
                ],
            },
            {
                'numero': 4, 'titulo': 'História Antiga',
                'locais': [
                    {'nome': 'Parque Histórico de Ayutthaya', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 14.3556, 'lng': 100.5604, 'notas': 'Parque histórico com ruínas de templos e palácios.'},
                ],
            },
        ],
    },
    {
        'slug': 'hong-kong-china',
        'titulo': 'Hong Kong em 3 Dias',
        'emoji': '🍷',
        'descricao': 'A união perfeita entre arranha-céus futuristas, tradição e vistas deslumbrantes.',
        'destino': 'Hong Kong, China',
        'dias': [
            {
                'numero': 1, 'titulo': 'Vistas Clássicas e o Porto',
                'locais': [
                    {'nome': 'Victoria Peak', 'tipo': 'turismo', 'emoji': '⛰️', 'lat': 22.2759, 'lng': 114.1455, 'notas': 'Melhor vista panorâmica de Hong Kong.'},
                    {'nome': 'Star Ferry (Central Pier)', 'tipo': 'turismo', 'emoji': '⛴️', 'lat': 22.2871, 'lng': 114.1622, 'notas': 'Travessia clássica entre Kowloon e Hong Kong Island.'},
                    {'nome': 'Lan Kwai Fong', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': 22.2809, 'lng': 114.1557, 'notas': 'Bairro de nightclubs e bares.'},
                ],
            },
            {
                'numero': 2, 'titulo': 'Natureza e Tradição',
                'locais': [
                    {'nome': 'Tian Tan Buddha (Ilha Lantau)', 'tipo': 'turismo', 'emoji': '🧘', 'lat': 22.2540, 'lng': 113.9050, 'notas': 'Buda de mármore na Ilha Lantau.'},
                    {'nome': 'Choi Hung Estate (Campo de Basquetebol)', 'tipo': 'turismo', 'emoji': '🏀', 'lat': 22.3352, 'lng': 114.2040, 'notas': 'Estação de basquetebol na zona nordeste de Hong Kong.'},
                ],
            },
            {
                'numero': 3, 'titulo': 'Luzes da Cidade',
                'locais': [
                    {'nome': 'Monster Building (Quarry Bay)', 'tipo': 'turismo', 'emoji': '🏢', 'lat': 22.2842, 'lng': 114.2123, 'notas': 'Edifício icônico de Hong Kong.'},
                    {'nome': 'Symphony of Lights (Tsim Sha Tsui)', 'tipo': 'turismo', 'emoji': '🎇', 'lat': 22.2936, 'lng': 114.1713, 'notas': 'Espectáculo de luzes no distrito de Tsim Sha Tsui.' },
                ],
            },
        ],
    },
    {
        'slug': 'macau-china',
        'titulo': 'Macau em 2 Dias',
        'emoji': '博彩',
        'descricao': 'Herança portuguesa, arquitetura histórica e grandiosidade da Las Vegas da Ásia.',
        'destino': 'Macau, China',
        'dias': [
            {
                'numero': 1, 'titulo': 'Herança portuguesa, arquitetura e a grandiosidade da Las Vegas da Ásia ',
                'locais': [
                    {'nome': 'Ruínas de São Paulo', 'tipo': 'turismo', 'emoji': '⛪', 'lat': 22.1976, 'lng': 113.5409, 'notas': 'Fachada de igreja do século XVII, símbolo de Macau.'},
                    {'nome': 'Largo do Senado', 'tipo': 'turismo', 'emoji': '⛲', 'lat': 22.1936, 'lng': 113.5398, 'notas': 'Praça central de Macau com arquitetura colonial.'},
                    {'nome': 'Fortalez do Monte', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 22.1970, 'lng': 113.5422 },
                ],
            },
            {
                'numero': 2, 'titulo': 'Luxo e Casinos no Cotai',
                'locais': [
                    {'nome': 'The Venetian Macao', 'tipo': 'turismo', 'emoji': '🎰', 'lat': 22.1466, 'lng': 113.5600 },
                    {'nome': 'The Londoner Macao', 'tipo': 'turismo', 'emoji': '🏛', 'lat': 22.1444, 'lng': 113.5630 },
                    {'nome': 'Club Cubic', 'tipo': 'nightlife', 'emoji': '🪩', 'lat': 22.1481, 'lng': 113.5661 },
                ],
            },
        ],
    },
    {
        'slug': 'singapura',
        'titulo': 'Singapura em 3 Dia',
        'emoji': '�',
        'descricao': 'Cidade-estado do futuro com jardins incriveis, cascatas interiores e luxo.',
        'destino': 'Singapura',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Futuro e o Luxo',
                'locais': [
                    {'nome': 'Gardens by the Bay', 'tipo': 'turismo', 'emoji': '🌳', 'lat': 1.2816, 'lng': 103.8636 },
                    {'nome': 'Marina Bay Sands', 'tipo': 'turismo', 'emoji': '🏢', 'lat': 1.2834, 'lng': 103.8607 },
                    {'nome': 'CÉ LA VI (Rooftop Bar)', 'tipo': 'nightlife', 'emoji': '🥂', 'lat': 1.2834, 'lng': 103.8607 },
                ],
            },
            {
                'numero': 2, 'titulo': 'Cultura e Arquitetura',
                'locais': [
                    {'nome': 'Parque Merlion', 'tipo': 'turismo', 'emoji': '🦁', 'lat': 1.2868, 'lng': 103.8545 },
                    {'nome': 'Old Hill Street Police Station', 'tipo': 'turismo', 'emoji': '🌈', 'lat': 1.2907, 'lng': 103.8465 },
                    {'nome': 'Clarke Quay', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': 1.2905, 'lng': 103.8466 },
                ],
            },
            {
                'numero': 3,
                'titulo': 'Diversão e Aeroporto Viral',
                'locais': [
                    {'nome': 'Jewel Changi Airport', 'tipo': 'turismo', 'emoji': '✈️', 'lat': 1.3602, 'lng': 103.9897},
                    {'nome': 'Universal Studios (Sentosa)', 'tipo': 'turismo', 'emoji': '🎢', 'lat': 1.2540, 'lng': 103.8238},
                ]
            },
        ],
    },
    {
        'slug': 'kuala-lumpur-malasia',
        'titulo': 'Kuala Lumpur em 3 Dias',
        'emoji': '🇲🇾',
        'descricao': 'Torres icónicas, grutas impressionantes e uma fusão cultural única.',
        'destino': 'Kuala Lumpur, Malásia',
        'dias': [
            {
                'numero': 1,
                'titulo': 'Torres e Luzes',
                'locais': [
                    {'nome': 'Torres Petronas', 'tipo': 'turismo', 'emoji': '🏙️', 'lat': 3.1578, 'lng': 101.7118},
                    {'nome': 'Saloma Link Bridge', 'tipo': 'turismo', 'emoji': '🌉', 'lat': 3.1610, 'lng': 101.7082},
                    {'nome': 'Heli Lounge Bar', 'tipo': 'nightlife', 'emoji': '🚁', 'lat': 3.1500, 'lng': 101.7107},
                ],
            },
            {
                'numero': 2,
                'titulo': 'Cavernas e Mercados',
                'locais': [
                    {'nome': 'Batu Caves', 'tipo': 'turismo', 'emoji': '🛕', 'lat': 3.2379, 'lng': 101.6830},
                    {'nome': 'Petaling Street (Chinatown)', 'tipo': 'compras', 'emoji': '🏮', 'lat': 3.1445, 'lng': 101.6973},
                    {'nome': 'Changkat Bukit Bintang', 'tipo': 'nightlife', 'emoji': '🍹', 'lat': 3.1477, 'lng': 101.7072},
                ],
            },
            {
                'numero': 3,
                'titulo': 'História e Panoramas',
                'locais': [
                    {'nome': 'Praça Merdeka', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 3.1488, 'lng': 101.6943},
                    {'nome': 'KL Tower (Menara KL)', 'tipo': 'turismo', 'emoji': '🗼', 'lat': 3.1528, 'lng': 101.7038},
                ],
            },
        ],
    },
    {
        'slug': 'londres-reino-unido',
        'titulo': 'Londres em 4 Dias',
        'emoji': '🇬🇧',
        'descricao': 'Monumentos reais, museus épicos e uma das melhores vidas noturnas da Europa.',
        'destino': 'Londres, Reino Unido',
        'dias': [
            {
                'numero': 1, 'titulo': 'Ícones Reais e o Rio',
                'locais': [
                    {'nome': 'Big Ben e Westminster', 'tipo': 'turismo', 'emoji': '🕰️', 'lat': 51.5007, 'lng': -0.1246},
                    {'nome': 'London Eye', 'tipo': 'turismo', 'emoji': '🎡', 'lat': 51.5033, 'lng': -0.1195},
                ],
            },
            {
                'numero': 2, 'titulo': 'História e Mercados',
                'locais': [
                    {'nome': 'Tower Bridge', 'tipo': 'turismo', 'emoji': '🌉', 'lat': 51.5055, 'lng': -0.0754},
                    {'nome': 'Borough Market', 'tipo': 'restaurante', 'emoji': '🍲', 'lat': 51.5051, 'lng': -0.0903},
                ],
            },
            {
                'numero': 3, 'titulo': 'Cultura e West End',
                'locais': [
                    {'nome': 'British Museum', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 51.5194, 'lng': -0.1270},
                    {'nome': 'Soho', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': 51.5136, 'lng': -0.1365},
                ],
            },
            {
                'numero': 4, 'titulo': 'Vibe Alternativa',
                'locais': [
                    {'nome': 'Camden Town', 'tipo': 'compras', 'emoji': '🎸', 'lat': 51.5390, 'lng': -0.1426},
                    {'nome': 'God\'s Own Junkyard', 'tipo': 'turismo', 'emoji': ' neon', 'lat': 51.5891, 'lng': 0.0076},
                ],
            },
        ],
    },
    {
        'slug': 'paris-franca',
        'titulo': 'Paris em 4 Dias',
        'emoji': '🇫🇷',
        'descricao': 'Arte, romance, arquitetura inesquecível e a magia de Montmartre.',
        'destino': 'Paris, França',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Cartão Postal',
                'locais': [
                    {'nome': 'Torre Eiffel', 'tipo': 'turismo', 'emoji': '🗼', 'lat': 48.8584, 'lng': 2.2945},
                    {'nome': 'Arco do Triunfo', 'tipo': 'turismo', 'emoji': '⛩️', 'lat': 48.8738, 'lng': 2.2950},
                ],
            },
            {
                'numero': 2, 'titulo': 'Coração da Arte',
                'locais': [
                    {'nome': 'Museu do Louvre', 'tipo': 'turismo', 'emoji': '🖼️', 'lat': 48.8606, 'lng': 2.3376},
                    {'nome': 'Rue de l\'Université', 'tipo': 'turismo', 'emoji': '📸', 'lat': 48.8600, 'lng': 2.3020},
                ],
            },
            {
                'numero': 3, 'titulo': 'Boémia e Cabarés',
                'locais': [
                    {'nome': 'Sacré-Cœur (Montmartre)', 'tipo': 'turismo', 'emoji': '⛪', 'lat': 48.8867, 'lng': 2.3431},
                    {'nome': 'Moulin Rouge (Pigalle)', 'tipo': 'nightlife', 'emoji': '💃', 'lat': 48.8841, 'lng': 2.3323},
                ],
            },
            {
                'numero': 4, 'titulo': 'Realeza Francesa',
                'locais': [
                    {'nome': 'Palácio de Versalhes', 'tipo': 'turismo', 'emoji': '👑', 'lat': 48.8014, 'lng': 2.1204},
                    {'nome': 'Le Marais', 'tipo': 'nightlife', 'emoji': '🥂', 'lat': 48.8588, 'lng': 2.3610},
                ],
            },
        ],
    },
    {
        'slug': 'istambul-turquia',
        'titulo': 'Istambul em 3 Dias',
        'emoji': '🇹🇷',
        'descricao': 'A ponte entre a Europa e a Ásia, cheia de mesquitas, mercados e chá.',
        'destino': 'Istambul, Turquia',
        'dias': [
            {
                'numero': 1, 'titulo': 'Impérios Antigos',
                'locais': [
                    {'nome': 'Hagia Sophia', 'tipo': 'turismo', 'emoji': '🕌', 'lat': 41.0082, 'lng': 28.9784},
                    {'nome': 'Mesquita Azul', 'tipo': 'turismo', 'emoji': '🕌', 'lat': 41.0054, 'lng': 28.9768},
                ],
            },
            {
                'numero': 2, 'titulo': 'Palácios e Compras',
                'locais': [
                    {'nome': 'Palácio Topkapi', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 41.0115, 'lng': 28.9834},
                    {'nome': 'Grand Bazaar', 'tipo': 'compras', 'emoji': '🛍️', 'lat': 41.0106, 'lng': 28.9680},
                ],
            },
            {
                'numero': 3, 'titulo': 'Vistas e Cores',
                'locais': [
                    {'nome': 'Torre Galata', 'tipo': 'turismo', 'emoji': '🗼', 'lat': 41.0256, 'lng': 28.9742},
                    {'nome': 'Bairro de Balat', 'tipo': 'turismo', 'emoji': '🏘️', 'lat': 41.0315, 'lng': 28.9469},
                    {'nome': 'Kadıköy', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': 40.9904, 'lng': 29.0207},
                ],
            },
        ],
    },
    {
        'slug': 'roma-italia',
        'titulo': 'Roma em 4 Dias',
        'emoji': '🇮🇹',
        'descricao': 'Um museu a céu aberto com a melhor massa e os monumentos mais épicos do mundo.',
        'destino': 'Roma, Itália',
        'dias': [
            {
                'numero': 1, 'titulo': 'Roma Antiga',
                'locais': [
                    {'nome': 'Coliseu', 'tipo': 'turismo', 'emoji': '🏟️', 'lat': 41.8902, 'lng': 12.4922},
                    {'nome': 'Fórum Romano', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 41.8925, 'lng': 12.4853},
                ],
            },
            {
                'numero': 2, 'titulo': 'O Estado do Vaticano',
                'locais': [
                    {'nome': 'Basílica de São Pedro', 'tipo': 'turismo', 'emoji': '⛪', 'lat': 41.9022, 'lng': 12.4539},
                    {'nome': 'Museus do Vaticano', 'tipo': 'turismo', 'emoji': '🖼️', 'lat': 41.9065, 'lng': 12.4536},
                ],
            },
            {
                'numero': 3, 'titulo': 'Fontes e Praças',
                'locais': [
                    {'nome': 'Fontana di Trevi', 'tipo': 'turismo', 'emoji': '⛲', 'lat': 41.9009, 'lng': 12.4833},
                    {'nome': 'Panteão', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 41.8986, 'lng': 12.4769},
                ],
            },
            {
                'numero': 4, 'titulo': 'Gastronomia e Boémia',
                'locais': [
                    {'nome': 'Osteria da Fortunata', 'tipo': 'restaurante', 'emoji': '🍝', 'lat': 41.8961, 'lng': 12.4718},
                    {'nome': 'Trastevere', 'tipo': 'nightlife', 'emoji': '🍷', 'lat': 41.8893, 'lng': 12.4697},
                ],
            },
        ],
    },
    {
        'slug': 'madrid-espanha',
        'titulo': 'Madrid em 3 Dias',
        'emoji': '🇪🇸',
        'descricao': 'Tapas, praças grandiosas e festas que só terminam quando o sol nasce.',
        'destino': 'Madrid, Espanha',
        'dias': [
            {
                'numero': 1, 'titulo': 'Realeza e Praças Clássicas',
                'locais': [
                    {'nome': 'Palácio Real', 'tipo': 'turismo', 'emoji': '👑', 'lat': 40.4180, 'lng': -3.7143},
                    {'nome': 'Plaza Mayor', 'tipo': 'turismo', 'emoji': '⛲', 'lat': 40.4154, 'lng': -3.7074},
                ],
            },
            {
                'numero': 2, 'titulo': 'Arte e Relaxamento',
                'locais': [
                    {'nome': 'Museu do Prado', 'tipo': 'turismo', 'emoji': '🖼️', 'lat': 40.4138, 'lng': -3.6921},
                    {'nome': 'Parque do Retiro', 'tipo': 'turismo', 'emoji': '🌳', 'lat': 40.4153, 'lng': -3.6845},
                ],
            },
            {
                'numero': 3, 'titulo': 'Rooftops e Churros',
                'locais': [
                    {'nome': 'Riu Plaza España (Terraço)', 'tipo': 'turismo', 'emoji': '🏙️', 'lat': 40.4233, 'lng': -3.7115},
                    {'nome': 'Chocolatería San Ginés', 'tipo': 'restaurante', 'emoji': '☕', 'lat': 40.4166, 'lng': -3.7067},
                    {'nome': 'Malasaña', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': 40.4261, 'lng': -3.7027},
                ],
            },
        ],
    },
    {
        'slug': 'marraquexe-marrocos',
        'titulo': 'Marraquexe em 3 Dias',
        'emoji': '🇲🇦',
        'descricao': 'Cores vibrantes, bazares labirínticos, jardins exuberantes e desertos.',
        'destino': 'Marraquexe, Marrocos',
        'dias': [
            {
                'numero': 1, 'titulo': 'A Medina Caótica',
                'locais': [
                    {'nome': 'Mesquita Koutoubia', 'tipo': 'turismo', 'emoji': '🕌', 'lat': 31.6240, 'lng': -7.9934},
                    {'nome': 'Praça Jemaa el-Fna', 'tipo': 'turismo', 'emoji': '🎭', 'lat': 31.6258, 'lng': -7.9892},
                ],
            },
            {
                'numero': 2, 'titulo': 'Beleza Majorelle e Palácios',
                'locais': [
                    {'nome': 'Jardim Majorelle', 'tipo': 'turismo', 'emoji': '🌵', 'lat': 31.6417, 'lng': -8.0028},
                    {'nome': 'Palácio Bahia', 'tipo': 'turismo', 'emoji': '🕌', 'lat': 31.6218, 'lng': -7.9836},
                ],
            },
            {
                'numero': 3, 'titulo': 'Glamour e Deserto',
                'locais': [
                    {'nome': 'Deserto de Agafay', 'tipo': 'turismo', 'emoji': '🏜️', 'lat': 31.4285, 'lng': -8.1472},
                    {'nome': 'Bairro de Gueliz', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': 31.6358, 'lng': -8.0123},
                ],
            },
        ],
    },
    {
        'slug': 'cairo-egito',
        'titulo': 'Cairo em 3 Dias',
        'emoji': '🇪🇬',
        'descricao': 'As pirâmides imponentes e a grandiosidade da história egípcia nas margens do Nilo.',
        'destino': 'Cairo, Egito',
        'dias': [
            {
                'numero': 1, 'titulo': 'A Grande Maravilha',
                'locais': [
                    {'nome': 'Pirâmides de Gizé', 'tipo': 'turismo', 'emoji': '🔺', 'lat': 29.9792, 'lng': 31.1342},
                    {'nome': '9 Pyramids Lounge', 'tipo': 'restaurante', 'emoji': '☕', 'lat': 29.9740, 'lng': 31.1300},
                ],
            },
            {
                'numero': 2, 'titulo': 'Faraós e Compras',
                'locais': [
                    {'nome': 'Grande Museu Egípcio', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 29.9947, 'lng': 31.1207},
                    {'nome': 'Khan el-Khalili', 'tipo': 'compras', 'emoji': '🏺', 'lat': 30.0478, 'lng': 31.2623},
                ],
            },
            {
                'numero': 3, 'titulo': 'Cidadela e Nilo Noturno',
                'locais': [
                    {'nome': 'Cidadela de Saladino', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 30.0298, 'lng': 31.2611},
                    {'nome': 'Zamalek (Cruzeiros no Nilo)', 'tipo': 'nightlife', 'emoji': '🛥️', 'lat': 30.0626, 'lng': 31.2200},
                ],
            },
        ],
    },
    {
        'slug': 'joanesburgo-africa-do-sul',
        'titulo': 'Joanesburgo em 2 Dias',
        'emoji': '🇿🇦',
        'descricao': 'Uma cidade de contrastes com um passado impactante e bairros de arte urbana.',
        'destino': 'Joanesburgo, África do Sul',
        'dias': [
            {
                'numero': 1, 'titulo': 'História e Consciência',
                'locais': [
                    {'nome': 'Museu do Apartheid', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': -26.2378, 'lng': 28.0022},
                    {'nome': 'Soweto (Tours)', 'tipo': 'turismo', 'emoji': '🏘️', 'lat': -26.2485, 'lng': 27.8540},
                ],
            },
            {
                'numero': 2, 'titulo': 'Arte Urbana e Vibes',
                'locais': [
                    {'nome': 'Constitution Hill', 'tipo': 'turismo', 'emoji': '⚖️', 'lat': -26.1901, 'lng': 28.0436},
                    {'nome': 'Maboneng Precinct', 'tipo': 'nightlife', 'emoji': '🎨', 'lat': -26.2025, 'lng': 28.0581},
                ],
            },
        ],
    },
    {
        'slug': 'cidade-do-cabo-africa-do-sul',
        'titulo': 'Cidade do Cabo em 4 Dias',
        'emoji': '🇿🇦',
        'descricao': 'Montanhas dramáticas, pinguins na praia e excelentes vinhos locais.',
        'destino': 'Cidade do Cabo, África do Sul',
        'dias': [
            {
                'numero': 1, 'titulo': 'A Montanha e o Porto',
                'locais': [
                    {'nome': 'Table Mountain', 'tipo': 'turismo', 'emoji': '⛰️', 'lat': -33.9628, 'lng': 18.4098},
                    {'nome': 'V&A Waterfront', 'tipo': 'compras', 'emoji': '🛍️', 'lat': -33.9036, 'lng': 18.4205},
                ],
            },
            {
                'numero': 2, 'titulo': 'Península e Pinguins',
                'locais': [
                    {'nome': 'Cabo da Boa Esperança', 'tipo': 'turismo', 'emoji': '🌊', 'lat': -34.3568, 'lng': 18.4719},
                    {'nome': 'Boulders Beach', 'tipo': 'turismo', 'emoji': '🐧', 'lat': -34.1970, 'lng': 18.4510},
                ],
            },
            {
                'numero': 3, 'titulo': 'Cores e Banhos',
                'locais': [
                    {'nome': 'Bo-Kaap', 'tipo': 'turismo', 'emoji': '🌈', 'lat': -33.9216, 'lng': 18.4133},
                    {'nome': 'Camps Bay', 'tipo': 'nightlife', 'emoji': '🌅', 'lat': -33.9515, 'lng': 18.3779},
                ],
            },
            {
                'numero': 4, 'titulo': 'Vinhos de Classe Mundial',
                'locais': [
                    {'nome': 'Stellenbosch (Rota dos Vinhos)', 'tipo': 'turismo', 'emoji': '🍷', 'lat': -33.9321, 'lng': 18.8602},
                ],
            },
        ],
    },
    {
        'slug': 'casablanca-marrocos',
        'titulo': 'Casablanca em 2 Dias',
        'emoji': '🇲🇦',
        'descricao': 'A capital económica com a sua imponente mesquita sobre o oceano e a nostalgia de Hollywood.',
        'destino': 'Casablanca, Marrocos',
        'dias': [
            {
                'numero': 1, 'titulo': 'Obra-prima à beira-mar',
                'locais': [
                    {'nome': 'Mesquita Hassan II', 'tipo': 'turismo', 'emoji': '🕌', 'lat': 33.6080, 'lng': -7.6327},
                    {'nome': 'La Corniche', 'tipo': 'turismo', 'emoji': '🏖️', 'lat': 33.5939, 'lng': -7.6628},
                ],
            },
            {
                'numero': 2, 'titulo': 'Cultura e Nostalgia',
                'locais': [
                    {'nome': 'Bairro Habous', 'tipo': 'compras', 'emoji': '🏺', 'lat': 33.5786, 'lng': -7.6049},
                    {'nome': 'Rick\'s Café', 'tipo': 'restaurante', 'emoji': '🎹', 'lat': 33.6047, 'lng': -7.6200},
                ],
            },
        ],
    },  
    {
        'slug': 'nova-iorque-eua',
        'titulo': 'Nova Iorque em 5 Dias',
        'emoji': '🇺🇸',
        'descricao': 'A cidade que nunca dorme: arranha-céus, cultura urbana e os locais mais famosos do cinema.',
        'destino': 'Nova Iorque, EUA',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Coração de Manhattan',
                'locais': [
                    {'nome': 'Times Square', 'tipo': 'turismo', 'emoji': '🚥', 'lat': 40.7580, 'lng': -73.9855},
                    {'nome': 'Central Park', 'tipo': 'turismo', 'emoji': '🌳', 'lat': 40.7812, 'lng': -73.9665},
                ]
            },
            {
                'numero': 2, 'titulo': 'Liberdade e Memória',
                'locais': [
                    {'nome': 'Estátua da Liberdade', 'tipo': 'turismo', 'emoji': '🗽', 'lat': 40.6892, 'lng': -74.0445},
                    {'nome': '9/11 Memorial', 'tipo': 'turismo', 'emoji': '🕊️', 'lat': 40.7115, 'lng': -74.0133},
                ]
            },
            {
                'numero': 3, 'titulo': 'Arte e High Line',
                'locais': [
                    {'nome': 'MoMA', 'tipo': 'turismo', 'emoji': '🖼️', 'lat': 40.7614, 'lng': -73.9776},
                    {'nome': 'Chelsea Market', 'tipo': 'restaurante', 'emoji': '🌮', 'lat': 40.7420, 'lng': -74.0048},
                ]
            },
            {
                'numero': 4, 'titulo': 'Atravessando para Brooklyn',
                'locais': [
                    {'nome': 'Brooklyn Bridge', 'tipo': 'turismo', 'emoji': '🌉', 'lat': 40.7061, 'lng': -73.9969},
                    {'nome': 'Washington Street (DUMBO)', 'tipo': 'turismo', 'emoji': '📸', 'lat': 40.7033, 'lng': -73.9896},
                ]
            },
            {
                'numero': 5, 'titulo': 'Alturas e Bares',
                'locais': [
                    {'nome': 'Summit One Vanderbilt', 'tipo': 'turismo', 'emoji': '☁️', 'lat': 40.7528, 'lng': -73.9771},
                    {'nome': 'West Village', 'tipo': 'nightlife', 'emoji': '🍷', 'lat': 40.7358, 'lng': -74.0036},
                ]
            }
        ]
    },
    {
        'slug': 'cancun-mexico',
        'titulo': 'Cancún em 4 Dias',
        'emoji': '🇲🇽',
        'descricao': 'Praias caribenhas, ruínas maias, grutas aquáticas e festas lendárias.',
        'destino': 'Cancún, México',
        'dias': [
            {
                'numero': 1, 'titulo': 'Caraíbas e Festa',
                'locais': [
                    {'nome': 'Praia Delfines (Zona Hoteleira)', 'tipo': 'turismo', 'emoji': '🏖️', 'lat': 21.0607, 'lng': -86.7795},
                    {'nome': 'Coco Bongo', 'tipo': 'nightlife', 'emoji': '🎉', 'lat': 21.1329, 'lng': -86.7469},
                ]
            },
            {
                'numero': 2, 'titulo': 'Maias e Cenotes',
                'locais': [
                    {'nome': 'Chichén Itzá', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 20.6843, 'lng': -88.5678},
                    {'nome': 'Cenote Suytun', 'tipo': 'turismo', 'emoji': '🕳️', 'lat': 20.6985, 'lng': -88.1225},
                ]
            },
            {
                'numero': 3, 'titulo': 'Ilha e Baloiços',
                'locais': [
                    {'nome': 'Isla Mujeres', 'tipo': 'turismo', 'emoji': '🏝️', 'lat': 21.2322, 'lng': -86.7323},
                ]
            },
            {
                'numero': 4, 'titulo': 'Natureza e Aventura',
                'locais': [
                    {'nome': 'Parque Xcaret', 'tipo': 'turismo', 'emoji': '🦜', 'lat': 20.5809, 'lng': -87.1197},
                ]
            }
        ]
    },
    {
        'slug': 'cidade-do-mexico-mexico',
        'titulo': 'Cidade do México em 4 Dias',
        'emoji': '🇲🇽',
        'descricao': 'Uma metrópole vibrante que junta pirâmides astecas, museus coloridos e gastronomia incrível.',
        'destino': 'Cidade do México, México',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Centro Histórico',
                'locais': [
                    {'nome': 'Zócalo e Catedral', 'tipo': 'turismo', 'emoji': '⛪', 'lat': 19.4326, 'lng': -99.1332},
                    {'nome': 'Templo Mayor', 'tipo': 'turismo', 'emoji': '🏛️', 'lat': 19.4349, 'lng': -99.1314},
                ]
            },
            {
                'numero': 2, 'titulo': 'A Cidade dos Deuses',
                'locais': [
                    {'nome': 'Pirâmides de Teotihuacán', 'tipo': 'turismo', 'emoji': '🔺', 'lat': 19.6925, 'lng': -98.8438},
                    {'nome': 'Basílica de Guadalupe', 'tipo': 'turismo', 'emoji': '📿', 'lat': 19.4848, 'lng': -99.1179},
                ]
            },
            {
                'numero': 3, 'titulo': 'Frida e Trajineras',
                'locais': [
                    {'nome': 'Museu Frida Kahlo (Coyoacán)', 'tipo': 'turismo', 'emoji': '🎨', 'lat': 19.3551, 'lng': -99.1625},
                    {'nome': 'Canais de Xochimilco', 'tipo': 'turismo', 'emoji': '🛶', 'lat': 19.2644, 'lng': -99.1036},
                ]
            },
            {
                'numero': 4, 'titulo': 'Design e Mezcal',
                'locais': [
                    {'nome': 'Biblioteca Vasconcelos', 'tipo': 'turismo', 'emoji': '📚', 'lat': 19.4468, 'lng': -99.1506},
                    {'nome': 'Roma Norte', 'tipo': 'nightlife', 'emoji': '🥃', 'lat': 19.4194, 'lng': -99.1606},
                ]
            }
        ]
    },
    {
        'slug': 'los-angeles-eua',
        'titulo': 'Los Angeles em 4 Dias',
        'emoji': '🇺🇸',
        'descricao': 'O epicentro do cinema, praias icónicas do sul da Califórnia e luxo a cada esquina.',
        'destino': 'Los Angeles, EUA',
        'dias': [
            {
                'numero': 1, 'titulo': 'As Estrelas',
                'locais': [
                    {'nome': 'Hollywood Walk of Fame', 'tipo': 'turismo', 'emoji': '⭐', 'lat': 34.1015, 'lng': -118.3267},
                    {'nome': 'Griffith Observatory', 'tipo': 'turismo', 'emoji': '🔭', 'lat': 34.1184, 'lng': -118.3004},
                ]
            },
            {
                'numero': 2, 'titulo': 'Cultura de Praia',
                'locais': [
                    {'nome': 'Santa Monica Pier', 'tipo': 'turismo', 'emoji': '🎡', 'lat': 34.0099, 'lng': -118.4960},
                    {'nome': 'Venice Beach', 'tipo': 'turismo', 'emoji': '🛹', 'lat': 33.9850, 'lng': -118.4695},
                ]
            },
            {
                'numero': 3, 'titulo': 'Magia e Luzes',
                'locais': [
                    {'nome': 'Universal Studios Hollywood', 'tipo': 'turismo', 'emoji': '🎬', 'lat': 34.1381, 'lng': -118.3534},
                    {'nome': 'Urban Light (LACMA)', 'tipo': 'turismo', 'emoji': '💡', 'lat': 34.0639, 'lng': -118.3592},
                ]
            },
            {
                'numero': 4, 'titulo': 'O Glamour',
                'locais': [
                    {'nome': 'Rodeo Drive', 'tipo': 'compras', 'emoji': '🛍️', 'lat': 34.0673, 'lng': -118.4024},
                    {'nome': 'West Hollywood (WeHo)', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': 34.0900, 'lng': -118.3617},
                ]
            }
        ]
    },
    {
        'slug': 'orlando-eua',
        'titulo': 'Orlando em 4 Dias',
        'emoji': '🇺🇸',
        'descricao': 'A capital mundial da diversão, parques temáticos épicos e compras sem fim.',
        'destino': 'Orlando, EUA',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Mundo Mágico',
                'locais': [
                    {'nome': 'Disney\'s Magic Kingdom', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 28.4178, 'lng': -81.5812},
                ]
            },
            {
                'numero': 2, 'titulo': 'Ação e Cinema',
                'locais': [
                    {'nome': 'Universal Studios (Diagon Alley)', 'tipo': 'turismo', 'emoji': '⚡', 'lat': 28.4777, 'lng': -81.4680},
                ]
            },
            {
                'numero': 3, 'titulo': 'Aventuras Épicas',
                'locais': [
                    {'nome': 'Islands of Adventure', 'tipo': 'turismo', 'emoji': '🎢', 'lat': 28.4712, 'lng': -81.4735},
                ]
            },
            {
                'numero': 4, 'titulo': 'Compras e Entretenimento',
                'locais': [
                    {'nome': 'Orlando International Premium Outlets', 'tipo': 'compras', 'emoji': '🛍️', 'lat': 28.4754, 'lng': -81.4503},
                    {'nome': 'Disney Springs', 'tipo': 'nightlife', 'emoji': '🍹', 'lat': 28.3712, 'lng': -81.5209},
                ]
            }
        ]
    },
    {
        'slug': 'buenos-aires-argentina',
        'titulo': 'Buenos Aires em 4 Dias',
        'emoji': '🇦🇷',
        'descricao': 'Arquitetura europeia, tango nas ruas, carne incrível e noites longas.',
        'destino': 'Buenos Aires, Argentina',
        'dias': [
            {
                'numero': 1, 'titulo': 'Centro Político e Histórico',
                'locais': [
                    {'nome': 'Obelisco', 'tipo': 'turismo', 'emoji': '🗼', 'lat': -34.6037, 'lng': -58.3816},
                    {'nome': 'Plaza de Mayo (Casa Rosada)', 'tipo': 'turismo', 'emoji': '🏢', 'lat': -34.6083, 'lng': -58.3712},
                ]
            },
            {
                'numero': 2, 'titulo': 'Cores e Tradição',
                'locais': [
                    {'nome': 'Caminito (La Boca)', 'tipo': 'turismo', 'emoji': '🎨', 'lat': -34.6394, 'lng': -58.3621},
                    {'nome': 'San Telmo', 'tipo': 'turismo', 'emoji': '💃', 'lat': -34.6196, 'lng': -58.3732},
                ]
            },
            {
                'numero': 3, 'titulo': 'Elegância e Literatura',
                'locais': [
                    {'nome': 'Cemitério da Recoleta', 'tipo': 'turismo', 'emoji': '🪦', 'lat': -34.5875, 'lng': -58.3927},
                    {'nome': 'El Ateneo Grand Splendid', 'tipo': 'turismo', 'emoji': '📖', 'lat': -34.5960, 'lng': -58.3941},
                ]
            },
            {
                'numero': 4, 'titulo': 'Parques e Noite',
                'locais': [
                    {'nome': 'Floralis Genérica', 'tipo': 'turismo', 'emoji': '🌸', 'lat': -34.5813, 'lng': -58.3934},
                    {'nome': 'Palermo Soho', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': -34.5886, 'lng': -58.4285},
                ]
            }
        ]
    },
    {
        'slug': 'rio-de-janeiro-brasil',
        'titulo': 'Rio de Janeiro em 4 Dias',
        'emoji': '🇧🇷',
        'descricao': 'Samba, praias deslumbrantes e algumas das maravilhas naturais mais famosas do mundo.',
        'destino': 'Rio de Janeiro, Brasil',
        'dias': [
            {
                'numero': 1, 'titulo': 'Maravilhas e Praias',
                'locais': [
                    {'nome': 'Cristo Redentor', 'tipo': 'turismo', 'emoji': '⛰️', 'lat': -22.9519, 'lng': -43.2105},
                    {'nome': 'Praia de Copacabana', 'tipo': 'turismo', 'emoji': '🏖️', 'lat': -22.9711, 'lng': -43.1822},
                ]
            },
            {
                'numero': 2, 'titulo': 'Vistas e Natureza',
                'locais': [
                    {'nome': 'Parque Lage', 'tipo': 'restaurante', 'emoji': '☕', 'lat': -22.9644, 'lng': -43.2081},
                    {'nome': 'Pão de Açúcar', 'tipo': 'turismo', 'emoji': '🚠', 'lat': -22.9492, 'lng': -43.1555},
                ]
            },
            {
                'numero': 3, 'titulo': 'Cores e Samba',
                'locais': [
                    {'nome': 'Escadaria Selarón', 'tipo': 'turismo', 'emoji': '🪜', 'lat': -22.9154, 'lng': -43.1795},
                    {'nome': 'Arcos da Lapa', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': -22.9135, 'lng': -43.1797},
                ]
            },
            {
                'numero': 4, 'titulo': 'Aventura e Charme',
                'locais': [
                    {'nome': 'Pedra do Telégrafo', 'tipo': 'turismo', 'emoji': '📸', 'lat': -23.0682, 'lng': -43.5599},
                    {'nome': 'Ipanema', 'tipo': 'nightlife', 'emoji': '🌅', 'lat': -22.9836, 'lng': -43.2045},
                ]
            }
        ]
    },
    {
        'slug': 'lima-peru',
        'titulo': 'Lima em 3 Dias',
        'emoji': '🇵🇪',
        'descricao': 'A capital gastronómica da América do Sul com uma rica herança colonial sobre as falésias.',
        'destino': 'Lima, Peru',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Centro Colonial',
                'locais': [
                    {'nome': 'Plaza de Armas', 'tipo': 'turismo', 'emoji': '⛲', 'lat': -12.0453, 'lng': -77.0311},
                    {'nome': 'Catacumbas de São Francisco', 'tipo': 'turismo', 'emoji': '💀', 'lat': -12.0450, 'lng': -77.0270},
                ]
            },
            {
                'numero': 2, 'titulo': 'Falésias e Ruínas',
                'locais': [
                    {'nome': 'Huaca Pucllana', 'tipo': 'turismo', 'emoji': '🧱', 'lat': -12.1102, 'lng': -77.0335},
                    {'nome': 'Malecón de Miraflores', 'tipo': 'turismo', 'emoji': '🚲', 'lat': -12.1265, 'lng': -77.0390},
                ]
            },
            {
                'numero': 3, 'titulo': 'Boémia e Pisco Sour',
                'locais': [
                    {'nome': 'Puente de los Suspiros', 'tipo': 'turismo', 'emoji': '🌉', 'lat': -12.1488, 'lng': -77.0232},
                    {'nome': 'Ayahuasca Restobar (Barranco)', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': -12.1481, 'lng': -77.0221},
                ]
            }
        ]
    },
    {
        'slug': 'sao-paulo-brasil',
        'titulo': 'São Paulo em 3 Dias',
        'emoji': '🇧🇷',
        'descricao': 'Uma selva de pedra gigantesca com uma arte urbana rica, miradouros e uma gastronomia de topo.',
        'destino': 'São Paulo, Brasil',
        'dias': [
            {
                'numero': 1, 'titulo': 'Avenida Imponente',
                'locais': [
                    {'nome': 'Avenida Paulista', 'tipo': 'turismo', 'emoji': '🚶', 'lat': -23.5615, 'lng': -46.6559},
                    {'nome': 'MASP', 'tipo': 'turismo', 'emoji': '🖼️', 'lat': -23.5615, 'lng': -46.6559},
                ]
            },
            {
                'numero': 2, 'titulo': 'Verde e Vidro',
                'locais': [
                    {'nome': 'Parque Ibirapuera', 'tipo': 'turismo', 'emoji': '🌳', 'lat': -23.5874, 'lng': -46.6576},
                    {'nome': 'Sampa Sky', 'tipo': 'turismo', 'emoji': '🏙️', 'lat': -23.5414, 'lng': -46.6346},
                ]
            },
            {
                'numero': 3, 'titulo': 'Grafite e Noite',
                'locais': [
                    {'nome': 'Beco do Batman', 'tipo': 'turismo', 'emoji': '🎨', 'lat': -23.5562, 'lng': -46.6865},
                    {'nome': 'Rua Augusta', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': -23.5574, 'lng': -46.6593},
                ]
            }
        ]
    },
    {
        'slug': 'cartagena-colombia',
        'titulo': 'Cartagena em 3 Dias',
        'emoji': '🇨🇴',
        'descricao': 'As cores do Caribe misturadas com varandas floridas, muralhas e salsa.',
        'destino': 'Cartagena, Colômbia',
        'dias': [
            {
                'numero': 1, 'titulo': 'Dentro das Muralhas',
                'locais': [
                    {'nome': 'Cidade Amuralhada', 'tipo': 'turismo', 'emoji': '🏰', 'lat': 10.4262, 'lng': -75.5510},
                    {'nome': 'Torre del Reloj', 'tipo': 'turismo', 'emoji': '🕰️', 'lat': 10.4233, 'lng': -75.5488},
                ]
            },
            {
                'numero': 2, 'titulo': 'Defesas e Rua',
                'locais': [
                    {'nome': 'Castelo de San Felipe', 'tipo': 'turismo', 'emoji': '🧱', 'lat': 10.4225, 'lng': -75.5398},
                    {'nome': 'Rua dos Guarda-chuvas (Getsemaní)', 'tipo': 'turismo', 'emoji': '☂️', 'lat': 10.4206, 'lng': -75.5463},
                ]
            },
            {
                'numero': 3, 'titulo': 'Ilhas e Pôr do Sol',
                'locais': [
                    {'nome': 'Islas del Rosario', 'tipo': 'turismo', 'emoji': '🏝️', 'lat': 10.1772, 'lng': -75.7601},
                    {'nome': 'Café del Mar', 'tipo': 'nightlife', 'emoji': '🌅', 'lat': 10.4251, 'lng': -75.5539},
                ]
            }
        ]
    },
    {
        'slug': 'sydney-australia',
        'titulo': 'Sydney em 4 Dias',
        'emoji': '🇦🇺',
        'descricao': 'A joia portuária da Austrália: arquitetura famosa, vida selvagem e praias épicas.',
        'destino': 'Sydney, Austrália',
        'dias': [
            {
                'numero': 1, 'titulo': 'O Porto Famoso',
                'locais': [
                    {'nome': 'Sydney Opera House', 'tipo': 'turismo', 'emoji': '🎭', 'lat': -33.8568, 'lng': 151.2153},
                    {'nome': 'Sydney Harbour Bridge', 'tipo': 'turismo', 'emoji': '🌉', 'lat': -33.8523, 'lng': 151.2108},
                ]
            },
            {
                'numero': 2, 'titulo': 'Vida de Praia',
                'locais': [
                    {'nome': 'Bondi Beach', 'tipo': 'turismo', 'emoji': '🏄', 'lat': -33.8915, 'lng': 151.2767},
                    {'nome': 'Bondi Icebergs Pool', 'tipo': 'turismo', 'emoji': '🏊', 'lat': -33.8943, 'lng': 151.2750},
                ]
            },
            {
                'numero': 3, 'titulo': 'Animais e Cais',
                'locais': [
                    {'nome': 'Taronga Zoo', 'tipo': 'turismo', 'emoji': '🐨', 'lat': -33.8436, 'lng': 151.2413},
                    {'nome': 'Darling Harbour', 'tipo': 'nightlife', 'emoji': '🎆', 'lat': -33.8749, 'lng': 151.1987},
                ]
            },
            {
                'numero': 4, 'titulo': 'Natureza e História',
                'locais': [
                    {'nome': 'Blue Mountains (Bate-e-volta)', 'tipo': 'turismo', 'emoji': '⛰️', 'lat': -33.7138, 'lng': 150.3117},
                    {'nome': 'The Rocks', 'tipo': 'nightlife', 'emoji': '🍺', 'lat': -33.8596, 'lng': 151.2086},
                ]
            }
        ]
    },
    {
        'slug': 'melbourne-australia',
        'titulo': 'Melbourne em 4 Dias',
        'emoji': '🇦🇺',
        'descricao': 'Cultura de café, ruelas artísticas, pinguins e praias coloridas.',
        'destino': 'Melbourne, Austrália',
        'dias': [
            {
                'numero': 1, 'titulo': 'Artes e Vielas',
                'locais': [
                    {'nome': 'Federation Square', 'tipo': 'turismo', 'emoji': '🏢', 'lat': -37.8180, 'lng': 144.9691},
                    {'nome': 'Hosier Lane (Street Art)', 'tipo': 'turismo', 'emoji': '🎨', 'lat': -37.8164, 'lng': 144.9691},
                ]
            },
            {
                'numero': 2, 'titulo': 'Jardins e Vistas',
                'locais': [
                    {'nome': 'Royal Botanic Gardens', 'tipo': 'turismo', 'emoji': '🌷', 'lat': -37.8304, 'lng': 144.9796},
                    {'nome': 'Eureka Skydeck', 'tipo': 'turismo', 'emoji': '🏙️', 'lat': -37.8213, 'lng': 144.9644},
                ]
            },
            {
                'numero': 3, 'titulo': 'Roadtrip Épica',
                'locais': [
                    {'nome': 'Great Ocean Road (12 Apóstolos)', 'tipo': 'turismo', 'emoji': '🌊', 'lat': -38.6657, 'lng': 143.1044},
                ]
            },
            {
                'numero': 4, 'titulo': 'Praia e Bares',
                'locais': [
                    {'nome': 'Brighton Bathing Boxes', 'tipo': 'turismo', 'emoji': '🛖', 'lat': -37.9189, 'lng': 144.9868},
                    {'nome': 'Fitzroy (Rooftops)', 'tipo': 'nightlife', 'emoji': '🎸', 'lat': -37.7981, 'lng': 144.9782},
                ]
            }
        ]
    },
    {
        'slug': 'auckland-nova-zelandia',
        'titulo': 'Auckland em 3 Dias',
        'emoji': '🇳🇿',
        'descricao': 'A "Cidade das Velas", construída sobre vulcões e rodeada por ilhas vinícolas.',
        'destino': 'Auckland, Nova Zelândia',
        'dias': [
            {
                'numero': 1, 'titulo': 'Torres e Porto',
                'locais': [
                    {'nome': 'Sky Tower', 'tipo': 'turismo', 'emoji': '🗼', 'lat': -36.8485, 'lng': 174.7622},
                    {'nome': 'Viaduct Harbour', 'tipo': 'restaurante', 'emoji': '🛥️', 'lat': -36.8415, 'lng': 174.7634},
                ]
            },
            {
                'numero': 2, 'titulo': 'Vinhos e Relaxamento',
                'locais': [
                    {'nome': 'Waiheke Island', 'tipo': 'turismo', 'emoji': '🍷', 'lat': -36.7869, 'lng': 175.0768},
                ]
            },
            {
                'numero': 3, 'titulo': 'Vulcões e Bares Cool',
                'locais': [
                    {'nome': 'Vulcão Mt Eden', 'tipo': 'turismo', 'emoji': '🌋', 'lat': -36.8778, 'lng': 174.7645},
                    {'nome': 'Ponsonby Road', 'tipo': 'nightlife', 'emoji': '🍸', 'lat': -36.8524, 'lng': 174.7441},
                ]
            }
        ]
    },
    {
        'slug': 'brisbane-gold-coast-australia',
        'titulo': 'Brisbane e Gold Coast em 4 Dias',
        'emoji': '🇦🇺',
        'descricao': 'Vida urbana descontraída com koalas, combinada com praias de surfistas e diversão.',
        'destino': 'Brisbane / Gold Coast, Austrália',
        'dias': [
            {
                'numero': 1, 'titulo': 'A Cidade e a Praia Falsa',
                'locais': [
                    {'nome': 'South Bank Parklands', 'tipo': 'turismo', 'emoji': '🏖️', 'lat': -27.4795, 'lng': 153.0205},
                    {'nome': 'Story Bridge', 'tipo': 'turismo', 'emoji': '🌉', 'lat': -27.4636, 'lng': 153.0357},
                ]
            },
            {
                'numero': 2, 'titulo': 'Koalas e Discotecas',
                'locais': [
                    {'nome': 'Santuário de Koalas Lone Pine', 'tipo': 'turismo', 'emoji': '🐨', 'lat': -27.5332, 'lng': 152.9686},
                    {'nome': 'Fortitude Valley (Brisbane)', 'tipo': 'nightlife', 'emoji': '🪩', 'lat': -27.4566, 'lng': 153.0357},
                ]
            },
            {
                'numero': 3, 'titulo': 'O Paraíso dos Surfistas',
                'locais': [
                    {'nome': 'Surfers Paradise (Gold Coast)', 'tipo': 'turismo', 'emoji': '🏄', 'lat': -28.0024, 'lng': 153.4299},
                    {'nome': 'Q1 Skypoint', 'tipo': 'turismo', 'emoji': '🏢', 'lat': -28.0068, 'lng': 153.4293},
                ]
            },
            {
                'numero': 4, 'titulo': 'Parques Temáticos',
                'locais': [
                    {'nome': 'Warner Bros Movie World', 'tipo': 'turismo', 'emoji': '🎢', 'lat': -27.8624, 'lng': 153.3121},
                ]
            }
        ]
    },
    {
        'slug': 'queenstown-nova-zelandia',
        'titulo': 'Queenstown em 3 Dias',
        'emoji': '🇳🇿',
        'descricao': 'A capital mundial da aventura: fiordes majestosos, bungees e hambúrgueres virais.',
        'destino': 'Queenstown, Nova Zelândia',
        'dias': [
            {
                'numero': 1, 'titulo': 'Alturas e Hambúrgueres',
                'locais': [
                    {'nome': 'Skyline Gondola', 'tipo': 'turismo', 'emoji': '🚠', 'lat': -45.0289, 'lng': 168.6548},
                    {'nome': 'Fergburger', 'tipo': 'restaurante', 'emoji': '🍔', 'lat': -45.0315, 'lng': 168.6601},
                ]
            },
            {
                'numero': 2, 'titulo': 'O Fiorde',
                'locais': [
                    {'nome': 'Milford Sound', 'tipo': 'turismo', 'emoji': '🏞️', 'lat': -44.6716, 'lng': 167.9256},
                ]
            },
            {
                'numero': 3, 'titulo': 'Relaxar e Sair',
                'locais': [
                    {'nome': 'Onsen Hot Pools', 'tipo': 'turismo', 'emoji': '♨️', 'lat': -44.9830, 'lng': 168.6675},
                    {'nome': 'The Mall', 'tipo': 'nightlife', 'emoji': '🍻', 'lat': -45.0318, 'lng': 168.6610},
                ]
            }
        ]
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
    roteiro_pk = request.GET.get('roteiro')
    waypoints_json = '[]'
    roteiro_titulo = ''
    if roteiro_pk:
        try:
            roteiro = Roteiro.objects.prefetch_related('dias__locais').get(pk=roteiro_pk, utilizador=request.user)
            roteiro_titulo = roteiro.titulo
            waypoints = []
            for dia in roteiro.dias.all():
                for local in dia.locais.all():
                    waypoints.append({
                        'lat': local.latitude,
                        'lng': local.longitude,
                        'nome': local.nome,
                    })
            waypoints_json = json.dumps(waypoints)
        except Roteiro.DoesNotExist:
            pass
    return render(request, 'mapa.html', {
        'api_key': settings.GEOAPIFY_API_KEY,
        'waypoints_json': waypoints_json,
        'roteiro_titulo': roteiro_titulo,
    })
