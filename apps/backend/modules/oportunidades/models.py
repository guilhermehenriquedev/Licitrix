"""
Modelos para o módulo de oportunidades.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal

class Edital(models.Model):
    """Modelo para editais de licitação."""
    
    ORIGEM_CHOICES = [
        ('portal', 'Portal Oficial'),
        ('upload', 'Upload Manual'),
        ('api', 'API Externa'),
        ('crawler', 'Crawler'),
    ]
    
    MODALIDADE_CHOICES = [
        ('pregao_eletronico', 'Pregão Eletrônico'),
        ('pregao_presencial', 'Pregão Presencial'),
        ('concorrencia', 'Concorrência'),
        ('tomada_precos', 'Tomada de Preços'),
        ('convite', 'Convite'),
        ('concurso', 'Concurso'),
        ('leilao', 'Leilão'),
        ('dispensa', 'Dispensa de Licitação'),
        ('inexigibilidade', 'Inexigibilidade de Licitação'),
    ]
    
    STATUS_INGESTAO_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro'),
    ]
    
    # Identificação
    numero = models.CharField('Número do Edital', max_length=100)
    ano = models.PositiveIntegerField('Ano')
    objeto = models.TextField('Objeto da Licitação')
    
    # Origem e processamento
    origem = models.CharField('Origem', max_length=20, choices=ORIGEM_CHOICES, default='upload')
    status_ingestao = models.CharField(
        'Status da Ingestão',
        max_length=20,
        choices=STATUS_INGESTAO_CHOICES,
        default='pendente'
    )
    
    # Órgão licitante
    orgao = models.CharField('Órgão Licitantante', max_length=200)
    uf = models.CharField('UF', max_length=2)
    municipio = models.CharField('Município', max_length=100)
    
    # Modalidade e valores
    modalidade = models.CharField('Modalidade', max_length=30, choices=MODALIDADE_CHOICES)
    valor_estimado = models.DecimalField(
        'Valor Estimado',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Datas importantes
    data_publicacao = models.DateField('Data de Publicação')
    data_abertura = models.DateField('Data de Abertura')
    data_encerramento = models.DateField('Data de Encerramento', null=True, blank=True)
    
    # Documentos
    arquivo_original = models.FileField('Arquivo Original', upload_to='editais/originais/')
    arquivo_processado = models.JSONField('Arquivo Processado', null=True, blank=True)
    
    # Metadados extraídos
    itens_extraidos = models.JSONField('Itens Extraídos', default=list, blank=True)
    documentos_exigidos = models.JSONField('Documentos Exigidos', default=list, blank=True)
    observacoes = models.TextField('Observações', blank=True)
    
    # Processamento IA
    parse_errors = models.JSONField('Erros de Parse', default=list, blank=True)
    confidence_score = models.DecimalField(
        'Score de Confiança',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    processed_at = models.DateTimeField('Processado em', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Edital'
        verbose_name_plural = 'Editais'
        db_table = 'oportunidades_edital'
        unique_together = ['numero', 'ano', 'orgao']
        indexes = [
            models.Index(fields=['status_ingestao']),
            models.Index(fields=['modalidade', 'uf']),
            models.Index(fields=['data_publicacao']),
            models.Index(fields=['valor_estimado']),
        ]
    
    def __str__(self):
        return f"{self.numero}/{self.ano} - {self.orgao}"
    
    @property
    def is_open(self):
        """Verifica se a licitação está aberta."""
        if not self.data_encerramento:
            return True
        return timezone.now().date() <= self.data_encerramento
    
    @property
    def days_until_deadline(self):
        """Retorna dias até o prazo final."""
        if not self.data_encerramento:
            return None
        delta = self.data_encerramento - timezone.now().date()
        return delta.days
    
    def mark_as_processed(self, confidence_score=None):
        """Marca o edital como processado."""
        self.status_ingestao = 'concluido'
        self.processed_at = timezone.now()
        if confidence_score:
            self.confidence_score = confidence_score
        self.save(update_fields=['status_ingestao', 'processed_at', 'confidence_score'])

class OportunidadeTenant(models.Model):
    """Modelo para oportunidades específicas de cada tenant."""
    
    STATUS_CHOICES = [
        ('nova', 'Nova'),
        ('analisando', 'Analisando'),
        ('proposta_enviada', 'Proposta Enviada'),
        ('vencedora', 'Vencedora'),
        ('perdida', 'Perdida'),
        ('desistiu', 'Desistiu'),
        ('cancelada', 'Cancelada'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='oportunidades')
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='oportunidades_tenant')
    
    # Status e acompanhamento
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='nova')
    match_score = models.DecimalField(
        'Score de Match',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Análise de relevância
    keywords_match = models.JSONField('Palavras-chave que Combinam', default=list, blank=True)
    relevancia_score = models.DecimalField(
        'Score de Relevância',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Decisão
    decisao = models.CharField('Decisão', max_length=50, blank=True)
    justificativa = models.TextField('Justificativa', blank=True)
    
    # Acompanhamento
    data_analise = models.DateTimeField('Data da Análise', null=True, blank=True)
    responsavel = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oportunidades_responsavel'
    )
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Oportunidade do Tenant'
        verbose_name_plural = 'Oportunidades dos Tenants'
        db_table = 'oportunidades_oportunidade_tenant'
        unique_together = ['tenant', 'edital']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['match_score']),
            models.Index(fields=['data_analise']),
        ]
    
    def __str__(self):
        return f"{self.edital} - {self.tenant.name}"
    
    @property
    def is_active(self):
        """Verifica se a oportunidade está ativa."""
        return self.status in ['nova', 'analisando', 'proposta_enviada']
    
    def update_status(self, new_status, responsavel=None, justificativa=None):
        """Atualiza o status da oportunidade."""
        self.status = new_status
        if responsavel:
            self.responsavel = responsavel
        if justificativa:
            self.justificativa = justificativa
        
        if new_status == 'analisando':
            self.data_analise = timezone.now()
        
        self.save(update_fields=['status', 'responsavel', 'justificativa', 'data_analise'])

class ItemEdital(models.Model):
    """Modelo para itens específicos do edital."""
    
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='itens')
    
    # Identificação
    codigo = models.CharField('Código', max_length=50)
    descricao = models.TextField('Descrição')
    especificacao_tecnica = models.TextField('Especificação Técnica', blank=True)
    
    # Quantidades e unidades
    quantidade = models.DecimalField(
        'Quantidade',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unidade = models.CharField('Unidade', max_length=20)
    
    # Valores
    valor_unitario_estimado = models.DecimalField(
        'Valor Unitário Estimado',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    valor_total_estimado = models.DecimalField(
        'Valor Total Estimado',
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Categorização
    categoria = models.CharField('Categoria', max_length=100, blank=True)
    subcategoria = models.CharField('Subcategoria', max_length=100, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        verbose_name = 'Item do Edital'
        verbose_name_plural = 'Itens do Edital'
        db_table = 'oportunidades_item_edital'
        indexes = [
            models.Index(fields=['edital', 'codigo']),
            models.Index(fields=['categoria', 'subcategoria']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.descricao[:50]}..."
    
    def save(self, *args, **kwargs):
        """Calcula valor total estimado automaticamente."""
        if self.valor_unitario_estimado and self.quantidade:
            self.valor_total_estimado = self.valor_unitario_estimado * self.quantidade
        super().save(*args, **kwargs)

class DocumentoExigido(models.Model):
    """Modelo para documentos exigidos no edital."""
    
    TIPO_CHOICES = [
        ('declaracao', 'Declaração'),
        ('certificado', 'Certificado'),
        ('contrato', 'Contrato'),
        ('procuracao', 'Procuração'),
        ('outro', 'Outro'),
    ]
    
    edital = models.ForeignKey(Edital, on_delete=models.CASCADE, related_name='documentos_exigidos')
    
    nome = models.CharField('Nome do Documento', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES, default='declaracao')
    descricao = models.TextField('Descrição', blank=True)
    obrigatorio = models.BooleanField('Obrigatório', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Documento Exigido'
        verbose_name_plural = 'Documentos Exigidos'
        db_table = 'oportunidades_documento_exigido'
    
    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
