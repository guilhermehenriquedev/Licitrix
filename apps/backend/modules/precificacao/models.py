"""
Modelos para o módulo de precificação.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class ItemProposta(models.Model):
    """Modelo para itens da proposta com precificação."""
    
    ESTRATEGIA_CHOICES = [
        ('competitiva', 'Competitiva'),
        ('moderada', 'Moderada'),
        ('conservadora', 'Conservadora'),
    ]
    
    oportunidade = models.ForeignKey(
        'oportunidades.OportunidadeTenant',
        on_delete=models.CASCADE,
        related_name='itens_proposta'
    )
    item_edital = models.ForeignKey(
        'oportunidades.ItemEdital',
        on_delete=models.CASCADE,
        related_name='propostas'
    )
    
    # Descrição e quantidades
    descricao = models.TextField('Descrição')
    unidade = models.CharField('Unidade', max_length=20)
    quantidade = models.DecimalField(
        'Quantidade',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Custos componentes
    custos_componentes = models.JSONField('Custos Componentes', default=dict)
    # Estrutura: {
    #   'mao_de_obra': {'valor': 10.50, 'unidade': 'hora'},
    #   'material': {'valor': 25.00, 'unidade': 'unidade'},
    #   'encargos': {'percentual': 40.0},
    #   'tributos': {'percentual': 15.0},
    #   'logistica': {'valor': 5.00, 'unidade': 'unidade'},
    #   'overhead': {'percentual': 10.0},
    #   'risco': {'percentual': 5.0}
    # }
    
    # Markup e estratégias
    markup_sugerido = models.DecimalField(
        'Markup Sugerido (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00')
    )
    
    # Preços por estratégia
    preco_competitivo = models.DecimalField(
        'Preço Competitivo',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    preco_moderado = models.DecimalField(
        'Preço Moderado',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    preco_conservador = models.DecimalField(
        'Preço Conservador',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Margens por estratégia
    margem_competitiva = models.DecimalField(
        'Margem Competitiva (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    margem_moderada = models.DecimalField(
        'Margem Moderada (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    margem_conservadora = models.DecimalField(
        'Margem Conservadora (%)',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Análise IA
    racional_ia = models.TextField('Racional da IA', blank=True)
    confidence_score = models.DecimalField(
        'Score de Confiança',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Histórico e benchmarking
    historico_precos = models.JSONField('Histórico de Preços', default=list, blank=True)
    benchmark_mercado = models.JSONField('Benchmark de Mercado', default=dict, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    calculated_at = models.DateTimeField('Calculado em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Item da Proposta'
        verbose_name_plural = 'Itens da Proposta'
        db_table = 'precificacao_item_proposta'
        unique_together = ['oportunidade', 'item_edital']
        indexes = [
            models.Index(fields=['oportunidade', 'preco_competitivo']),
            models.Index(fields=['markup_sugerido']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"{self.item_edital.codigo} - {self.descricao[:50]}..."
    
    @property
    def custo_total_unitario(self):
        """Calcula o custo total unitário."""
        if not self.custos_componentes:
            return Decimal('0.00')
        
        custo_total = Decimal('0.00')
        
        for componente, dados in self.custos_componentes.items():
            if 'valor' in dados:
                custo_total += Decimal(str(dados['valor']))
            elif 'percentual' in dados and 'base' in dados:
                base = Decimal(str(dados['base']))
                percentual = Decimal(str(dados['percentual'])) / Decimal('100.00')
                custo_total += base * percentual
        
        return custo_total
    
    @property
    def custo_total(self):
        """Calcula o custo total para a quantidade."""
        return self.custo_total_unitario * self.quantidade
    
    def calcular_precos(self):
        """Calcula preços para todas as estratégias."""
        custo_unitario = self.custo_total_unitario
        
        # Estratégia Competitiva (margem baixa)
        markup_competitivo = self.markup_sugerido * Decimal('0.7')  # 70% do markup sugerido
        self.preco_competitivo = custo_unitario * (Decimal('1.00') + markup_competitivo / Decimal('100.00'))
        self.margem_competitiva = markup_competitivo
        
        # Estratégia Moderada (margem média)
        self.preco_moderado = custo_unitario * (Decimal('1.00') + self.markup_sugerido / Decimal('100.00'))
        self.margem_moderada = self.markup_sugerido
        
        # Estratégia Conservadora (margem alta)
        markup_conservador = self.markup_sugerido * Decimal('1.3')  # 130% do markup sugerido
        self.preco_conservador = custo_unitario * (Decimal('1.00') + markup_conservador / Decimal('100.00'))
        self.margem_conservadora = markup_conservador
        
        self.calculated_at = timezone.now()
        self.save()

class CustoPadrao(models.Model):
    """Modelo para custos padrão por categoria."""
    
    CATEGORIA_CHOICES = [
        ('mao_de_obra', 'Mão de Obra'),
        ('material', 'Material'),
        ('equipamento', 'Equipamento'),
        ('servico', 'Serviço'),
        ('logistica', 'Logística'),
        ('overhead', 'Overhead'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='custos_padrao')
    
    categoria = models.CharField('Categoria', max_length=20, choices=CATEGORIA_CHOICES)
    nome = models.CharField('Nome', max_length=200)
    descricao = models.TextField('Descrição', blank=True)
    
    # Valores
    valor = models.DecimalField('Valor', max_digits=15, decimal_places=2)
    unidade = models.CharField('Unidade', max_length=20)
    tipo_valor = models.CharField('Tipo de Valor', max_length=20, choices=[
        ('unitario', 'Unitário'),
        ('percentual', 'Percentual'),
        ('fixo', 'Fixo'),
    ])
    
    # Aplicabilidade
    cnae_aplicavel = models.JSONField('CNAEs Aplicáveis', default=list, blank=True)
    uf_aplicavel = models.JSONField('UFs Aplicáveis', default=list, blank=True)
    
    # Validade
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    is_active = models.BooleanField('Ativo', default=True)
    
    class Meta:
        verbose_name = 'Custo Padrão'
        verbose_name_plural = 'Custos Padrão'
        db_table = 'precificacao_custo_padrao'
        unique_together = ['tenant', 'categoria', 'nome']
        indexes = [
            models.Index(fields=['tenant', 'categoria']),
            models.Index(fields=['cnae_aplicavel']),
            models.Index(fields=['uf_aplicavel']),
        ]
    
    def __str__(self):
        return f"{self.get_categoria_display()} - {self.nome}"
    
    @property
    def is_valid(self):
        """Verifica se o custo está válido para a data atual."""
        hoje = timezone.now().date()
        if self.data_fim and hoje > self.data_fim:
            return False
        return hoje >= self.data_inicio and self.is_active

class HistoricoPrecos(models.Model):
    """Modelo para histórico de preços vencedores."""
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='historico_precos')
    
    # Identificação
    descricao_item = models.CharField('Descrição do Item', max_length=500)
    categoria = models.CharField('Categoria', max_length=100)
    subcategoria = models.CharField('Subcategoria', max_length=100, blank=True)
    
    # Valores
    preco_unitario = models.DecimalField('Preço Unitário', max_digits=15, decimal_places=2)
    quantidade = models.DecimalField('Quantidade', max_digits=10, decimal_places=2)
    valor_total = models.DecimalField('Valor Total', max_digits=15, decimal_places=2)
    
    # Contexto
    orgao = models.CharField('Órgão', max_length=200)
    uf = models.CharField('UF', max_length=2)
    modalidade = models.CharField('Modalidade', max_length=50)
    data_licitacao = models.DateField('Data da Licitação')
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    fonte = models.CharField('Fonte', max_length=100, default='manual')
    
    class Meta:
        verbose_name = 'Histórico de Preços'
        verbose_name_plural = 'Históricos de Preços'
        db_table = 'precificacao_historico_precos'
        indexes = [
            models.Index(fields=['tenant', 'categoria']),
            models.Index(fields=['uf', 'modalidade']),
            models.Index(fields=['data_licitacao']),
            models.Index(fields=['preco_unitario']),
        ]
    
    def __str__(self):
        return f"{self.descricao_item[:50]}... - {self.orgao} ({self.data_licitacao})"
    
    def save(self, *args, **kwargs):
        """Calcula valor total automaticamente."""
        if self.preco_unitario and self.quantidade:
            self.valor_total = self.preco_unitario * self.quantidade
        super().save(*args, **kwargs)
