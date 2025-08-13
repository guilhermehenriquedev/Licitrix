"""
Modelos para o módulo de contratos.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Contrato(models.Model):
    """Modelo para contratos de licitação."""
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('suspenso', 'Suspenso'),
        ('encerrado', 'Encerrado'),
        ('rescindido', 'Rescindido'),
        ('prorrogado', 'Prorrogado'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='contratos')
    oportunidade = models.ForeignKey(
        'oportunidades.OportunidadeTenant',
        on_delete=models.CASCADE,
        related_name='contratos'
    )
    
    # Identificação
    numero = models.CharField('Número do Contrato', max_length=100)
    objeto = models.TextField('Objeto do Contrato')
    
    # Valores
    valor_total = models.DecimalField(
        'Valor Total',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_original = models.DecimalField(
        'Valor Original',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Datas
    data_inicio = models.DateField('Data de Início')
    data_fim = models.DateField('Data de Fim')
    data_assinatura = models.DateField('Data de Assinatura')
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='ativo')
    percentual_executado = models.DecimalField(
        'Percentual Executado (%)',
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Fiscalização
    fiscal_nome = models.CharField('Nome do Fiscal', max_length=200)
    fiscal_telefone = models.CharField('Telefone do Fiscal', max_length=20, blank=True)
    fiscal_email = models.EmailField('Email do Fiscal', blank=True)
    
    # SLAs e garantias
    slas = models.JSONField('SLAs', default=dict, blank=True)
    garantias = models.JSONField('Garantias', default=list, blank=True)
    
    # Documentos
    arquivo_contrato = models.FileField('Arquivo do Contrato', upload_to='contratos/', blank=True)
    anexos = models.JSONField('Anexos', default=list, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='contratos_criados'
    )
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        db_table = 'contratos_contrato'
        unique_together = ['tenant', 'numero']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['data_inicio', 'data_fim']),
            models.Index(fields=['valor_total']),
        ]
    
    def __str__(self):
        return f"{self.numero} - {self.objeto[:50]}..."
    
    @property
    def is_active(self):
        """Verifica se o contrato está ativo."""
        return self.status == 'ativo'
    
    @property
    def days_remaining(self):
        """Retorna dias restantes do contrato."""
        delta = self.data_fim - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def is_overdue(self):
        """Verifica se o contrato está vencido."""
        return timezone.now().date() > self.data_fim
    
    def update_percentual_executado(self):
        """Atualiza percentual executado baseado nas medições."""
        medicoes = self.medicoes.all()
        if medicoes.exists():
            total_percentual = sum(m.percentual for m in medicoes)
            self.percentual_executado = min(total_percentual, Decimal('100.00'))
            self.save(update_fields=['percentual_executado'])

class Medicao(models.Model):
    """Modelo para medições de execução contratual."""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada'),
        ('paga', 'Paga'),
    ]
    
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='medicoes')
    
    # Identificação
    numero = models.CharField('Número da Medição', max_length=50)
    competencia = models.CharField('Competência', max_length=7)  # YYYY-MM
    descricao = models.TextField('Descrição dos Serviços')
    
    # Valores
    percentual = models.DecimalField(
        'Percentual (%)',
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor = models.DecimalField(
        'Valor',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_medicao = models.DateField('Data da Medição')
    data_apresentacao = models.DateField('Data de Apresentação')
    data_aprovacao = models.DateField('Data de Aprovação', null=True, blank=True)
    
    # Fiscalização
    fiscal_observacoes = models.TextField('Observações do Fiscal', blank=True)
    fiscal_aprovado_por = models.CharField('Aprovado por', max_length=200, blank=True)
    
    # Evidências
    evidencias = models.JSONField('Evidências', default=list, blank=True)
    # Estrutura: [
    #   {'tipo': 'foto', 'arquivo': 'path/to/file.jpg', 'descricao': 'Descrição'},
    #   {'tipo': 'documento', 'arquivo': 'path/to/file.pdf', 'descricao': 'Descrição'}
    # ]
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='medicoes_criadas'
    )
    
    class Meta:
        verbose_name = 'Medição'
        verbose_name_plural = 'Medições'
        db_table = 'contratos_medicao'
        unique_together = ['contrato', 'numero']
        indexes = [
            models.Index(fields=['contrato', 'status']),
            models.Index(fields=['competencia']),
            models.Index(fields=['data_medicao']),
        ]
        ordering = ['-competencia', '-numero']
    
    def __str__(self):
        return f"{self.numero} - {self.competencia} ({self.contrato.numero})"
    
    @property
    def is_approved(self):
        """Verifica se a medição foi aprovada."""
        return self.status == 'aprovada'
    
    @property
    def is_paid(self):
        """Verifica se a medição foi paga."""
        return self.status == 'paga'
    
    def approve(self, fiscal_name):
        """Aprova a medição."""
        self.status = 'aprovada'
        self.data_aprovacao = timezone.now().date()
        self.fiscal_aprovado_por = fiscal_name
        self.save(update_fields=['status', 'data_aprovacao', 'fiscal_aprovado_por'])
        
        # Atualiza percentual executado do contrato
        self.contrato.update_percentual_executado()

class ItemContrato(models.Model):
    """Modelo para itens específicos do contrato."""
    
    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='itens')
    item_proposta = models.ForeignKey(
        'precificacao.ItemProposta',
        on_delete=models.CASCADE,
        related_name='itens_contrato'
    )
    
    # Descrição e quantidades
    descricao = models.TextField('Descrição')
    unidade = models.CharField('Unidade', max_length=20)
    quantidade_contratada = models.DecimalField(
        'Quantidade Contratada',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    quantidade_executada = models.DecimalField(
        'Quantidade Executada',
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Valores
    preco_unitario = models.DecimalField(
        'Preço Unitário',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_total = models.DecimalField(
        'Valor Total',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Item do Contrato'
        verbose_name_plural = 'Itens do Contrato'
        db_table = 'contratos_item_contrato'
        unique_together = ['contrato', 'item_proposta']
    
    def __str__(self):
        return f"{self.descricao[:50]}... - {self.contrato.numero}"
    
    @property
    def percentual_executado(self):
        """Calcula percentual executado do item."""
        if self.quantidade_contratada == 0:
            return Decimal('0.00')
        return (self.quantidade_executada / self.quantidade_contratada) * Decimal('100.00')
    
    @property
    def valor_executado(self):
        """Calcula valor executado do item."""
        return self.preco_unitario * self.quantidade_executada
    
    def save(self, *args, **kwargs):
        """Calcula valor total automaticamente."""
        if self.preco_unitario and self.quantidade_contratada:
            self.valor_total = self.preco_unitario * self.quantidade_contratada
        super().save(*args, **kwargs)
