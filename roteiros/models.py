from django.db import models
from django.contrib.auth.models import User

class Roteiro(models.Model):
    utilizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roteiros')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

class Dia(models.Model):
    roteiro = models.ForeignKey(Roteiro, on_delete=models.CASCADE, related_name='dias')
    numero = models.PositiveIntegerField()
    titulo = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['numero']

    def __str__(self):
        return f"Dia {self.numero} - {self.roteiro.titulo}"

class Local(models.Model):
    TIPO_CHOICES = [
        ('turismo', 'Turismo'),
        ('restaurante', 'Restaurante'),
        ('hotel', 'Hotel'),
        ('hospital', 'Hospital'),
        ('farmacia', 'Farmácia'),
        ('carregador', 'Carregador Elétrico'),
        ('outro', 'Outro'),
    ]

    dia = models.ForeignKey(Dia, on_delete=models.CASCADE, related_name='locais')
    nome = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='turismo')
    latitude = models.FloatField()
    longitude = models.FloatField()
    ordem = models.PositiveIntegerField(default=0)
    notas = models.TextField(blank=True)

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return self.nome