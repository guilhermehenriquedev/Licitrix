"""
Modelos para o módulo financeiro.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Fatura(models.Model):
    """Modelo para faturas de contratos."""
    
    STATUS_CHOICES = [
        ('rascunho', 'Rascunho'),
        ('emitida', 'Emitida'),
        ('enviada', 'Enviada'),
        ('recebida', 'Recebida'),
        ('paga', 'Paga'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
    
    TIPO_CHOICES = [
        ('medicao', 'Medição'),
        ('adicional', 'Adicional'),
        ('reajuste', 'Reajuste'),
        ('multa', 'Multa'),
        ('outro', 'Outro'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='faturas')
    contrato = models.ForeignKey('contratos.Contrato', on_delete=models.CASCADE, related_name='faturas')
    medicao = models.ForeignKey(
        'contratos.Medicao',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faturas'
    )
    
    # Identificação
    numero = models.CharField('Número da Fatura', max_length=100)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='medicao')
    descricao = models.TextField('Descrição')
    
    # Valores
    valor = models.DecimalField(
        'Valor',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    valor_liquido = models.DecimalField(
        'Valor Líquido',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Datas
    data_emissao = models.DateField('Data de Emissão')
    data_vencimento = models.DateField('Data de Vencimento')
    data_pagamento = models.DateField('Data de Pagamento', null=True, blank=True)
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='rascunho')
    dias_vencimento = models.IntegerField('Dias de Vencimento', default=30)
    
    # NF-e
    nf_chave = models.CharField('Chave da NF-e', max_length=50, blank=True)
    nf_numero = models.CharField('Número da NF-e', max_length=20, blank=True)
    nf_serie = models.CharField('Série da NF-e', max_length=10, blank=True)
    nf_protocolo = models.CharField('Protocolo da NF-e', max_length=50, blank=True)
    
    # Retenções
    retencoes = models.JSONField('Retenções', default=dict, blank=True)
    # Estrutura: {
    #   'ir': {'percentual': 1.5, 'valor': 150.00},
    #   'pis': {'percentual': 0.65, 'valor': 65.00},
    #   'cofins': {'percentual': 3.0, 'valor': 300.00},
    #   'csll': {'percentual': 1.0, 'valor': 100.00},
    #   'iss': {'percentual': 5.0, 'valor': 500.00}
    # }
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='faturas_criadas'
    )
    
    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        db_table = 'financeiro_fatura'
        unique_together = ['tenant', 'numero']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['contrato', 'medicao']),
            models.Index(fields=['data_vencimento']),
            models.Index(fields=['nf_chave']),
        ]
        ordering = ['-data_emissao']
    
    def __str__(self):
        return f"{self.numero} - {self.contrato.numero} - R$ {self.valor}"
    
    @property
    def is_overdue(self):
        """Verifica se a fatura está vencida."""
        return self.status not in ['paga', 'cancelada'] and timezone.now().date() > self.data_vencimento
    
    @property
    def days_overdue(self):
        """Retorna dias de atraso."""
        if not self.is_overdue:
            return 0
        delta = timezone.now().date() - self.data_vencimento
        return delta.days
    
    @property
    def valor_retido(self):
        """Calcula valor total retido."""
        if not self.retencoes:
            return Decimal('0.00')
        
        total_retido = Decimal('0.00')
        for retencao in self.retencoes.values():
            if 'valor' in retencao:
                total_retido += Decimal(str(retencao['valor']))
        
        return total_retido
    
    def calcular_valor_liquido(self):
        """Calcula valor líquido da fatura."""
        self.valor_liquido = self.valor - self.valor_retido
        self.save(update_fields=['valor_liquido'])
    
    def emitir_nf(self):
        """Marca fatura como NF emitida."""
        self.status = 'emitida'
        self.save(update_fields=['status'])
    
    def marcar_como_paga(self, data_pagamento=None):
        """Marca fatura como paga."""
        self.status = 'paga'
        if data_pagamento:
            self.data_pagamento = data_pagamento
        else:
            self.data_pagamento = timezone.now().date()
        self.save(update_fields=['status', 'data_pagamento'])

class CobrancaEvento(models.Model):
    """Modelo para eventos de cobrança."""
    
    TIPO_CHOICES = [
        ('lembrete', 'Lembrete'),
        ('cobranca', 'Cobrança'),
        ('resposta', 'Resposta'),
        ('acordo', 'Acordo'),
        ('protesto', 'Protesto'),
    ]
    
    CANAL_CHOICES = [
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('telefone', 'Telefone'),
        ('correio', 'Correio'),
        ('pessoal', 'Pessoal'),
    ]
    
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='eventos_cobranca')
    
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    canal = models.CharField('Canal', max_length=20, choices=CANAL_CHOICES)
    
    # Detalhes
    titulo = models.CharField('Título', max_length=200)
    mensagem = models.TextField('Mensagem')
    destinatario = models.CharField('Destinatário', max_length=200)
    
    # Status
    status = models.CharField('Status', max_length=20, choices=[
        ('pendente', 'Pendente'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('lido', 'Lido'),
        ('respondido', 'Respondido'),
        ('erro', 'Erro'),
    ], default='pendente')
    
    # Resposta
    resposta = models.TextField('Resposta', blank=True)
    data_resposta = models.DateTimeField('Data da Resposta', null=True, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    enviado_at = models.DateTimeField('Enviado em', null=True, blank=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_cobranca_criados'
    )
    
    class Meta:
        verbose_name = 'Evento de Cobrança'
        verbose_name_plural = 'Eventos de Cobrança'
        db_table = 'financeiro_cobranca_evento'
        indexes = [
            models.Index(fields=['fatura', 'tipo']),
            models.Index(fields=['canal', 'status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.fatura.numero} - {self.canal}"
    
    def marcar_como_enviado(self):
        """Marca evento como enviado."""
        self.status = 'enviado'
        self.enviado_at = timezone.now()
        self.save(update_fields=['status', 'enviado_at'])
    
    def registrar_resposta(self, resposta):
        """Registra resposta do cliente."""
        self.resposta = resposta
        self.status = 'respondido'
        self.data_resposta = timezone.now()
        self.save(update_fields=['resposta', 'status', 'data_resposta'])

class FluxoCaixa(models.Model):
    """Modelo para controle de fluxo de caixa."""
    
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]
    
    CATEGORIA_CHOICES = [
        ('faturamento', 'Faturamento'),
        ('pagamento_fornecedor', 'Pagamento a Fornecedor'),
        ('despesa_operacional', 'Despesa Operacional'),
        ('investimento', 'Investimento'),
        ('financiamento', 'Financiamento'),
        ('outro', 'Outro'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='fluxo_caixa')
    
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    categoria = models.CharField('Categoria', max_length=30, choices=CATEGORIA_CHOICES)
    
    # Valores
    valor = models.DecimalField(
        'Valor',
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    # Referências
    fatura = models.ForeignKey(
        Fatura,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fluxo_caixa'
    )
    contrato = models.ForeignKey(
        'contratos.Contrato',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fluxo_caixa'
    )
    
    # Datas
    data_prevista = models.DateField('Data Prevista')
    data_realizada = models.DateField('Data Realizada', null=True, blank=True)
    
    # Descrição
    descricao = models.TextField('Descrição')
    observacoes = models.TextField('Observações', blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='fluxo_caixa_criado'
    )
    
    class Meta:
        verbose_name = 'Fluxo de Caixa'
        verbose_name_plural = 'Fluxo de Caixa'
        db_table = 'financeiro_fluxo_caixa'
        indexes = [
            models.Index(fields=['tenant', 'tipo']),
            models.Index(fields=['categoria', 'data_prevista']),
            models.Index(fields=['fatura', 'contrato']),
        ]
        ordering = ['-data_prevista']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.categoria} - R$ {self.valor} - {self.data_prevista}"
    
    @property
    def is_realizado(self):
        """Verifica se o fluxo foi realizado."""
        return self.data_realizada is not None
    
    @property
    def is_entrada(self):
        """Verifica se é entrada de caixa."""
        return self.tipo == 'entrada'
    
    @property
    def is_saida(self):
        """Verifica se é saída de caixa."""
        return self.tipo == 'saida'
    
    def realizar(self, data_realizada=None):
        """Marca fluxo como realizado."""
        if data_realizada:
            self.data_realizada = data_realizada
        else:
            self.data_realizada = timezone.now().date()
        self.save(update_fields=['data_realizada'])
