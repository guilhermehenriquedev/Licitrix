"""
Modelos para o módulo de documentos.
"""
from django.db import models
from django.utils import timezone

class TemplateDoc(models.Model):
    """Modelo para templates de documentos."""
    
    TIPO_CHOICES = [
        ('planilha_precos', 'Planilha de Preços'),
        ('declaracao_me_epp', 'Declaração ME/EPP'),
        ('declaracao_falencia', 'Declaração de Falência'),
        ('declaracao_improbidade', 'Declaração de Improbidade'),
        ('declaracao_cumprimento', 'Declaração de Cumprimento'),
        ('proposta_comercial', 'Proposta Comercial'),
        ('termo_compromisso', 'Termo de Compromisso'),
        ('outro', 'Outro'),
    ]
    
    FORMATO_CHOICES = [
        ('xlsx', 'Excel (XLSX)'),
        ('docx', 'Word (DOCX)'),
        ('pdf', 'PDF'),
        ('html', 'HTML'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='templates_doc')
    
    nome = models.CharField('Nome do Template', max_length=200)
    tipo = models.CharField('Tipo', max_length=30, choices=TIPO_CHOICES)
    formato = models.CharField('Formato', max_length=10, choices=FORMATO_CHOICES)
    
    # Arquivo do template
    arquivo_template = models.FileField('Arquivo do Template', upload_to='templates/')
    
    # Configurações
    orgao_aplicavel = models.CharField('Órgão Aplicável', max_length=200, blank=True)
    modalidade_aplicavel = models.CharField('Modalidade Aplicável', max_length=50, blank=True)
    uf_aplicavel = models.CharField('UF Aplicável', max_length=2, blank=True)
    
    # Schema de campos
    schema_campos = models.JSONField('Schema de Campos', default=dict, blank=True)
    # Estrutura: {
    #   'campos_obrigatorios': ['cnpj', 'razao_social', 'objeto'],
    #   'campos_opcionais': ['observacoes', 'anexos'],
    #   'validacoes': {
    #     'cnpj': {'tipo': 'cnpj', 'obrigatorio': True},
    #     'valor_total': {'tipo': 'decimal', 'min': 0}
    #   }
    # }
    
    # Versão e controle
    versao = models.CharField('Versão', max_length=20, default='1.0')
    is_active = models.BooleanField('Ativo', default=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='templates_criados'
    )
    
    class Meta:
        verbose_name = 'Template de Documento'
        verbose_name_plural = 'Templates de Documentos'
        db_table = 'documentos_template_doc'
        unique_together = ['tenant', 'nome', 'versao']
        indexes = [
            models.Index(fields=['tenant', 'tipo']),
            models.Index(fields=['formato', 'is_active']),
            models.Index(fields=['orgao_aplicavel', 'modalidade_aplicavel']),
        ]
    
    def __str__(self):
        return f"{self.nome} v{self.versao} ({self.get_formato_display()})"
    
    @property
    def extensao_arquivo(self):
        """Retorna extensão do arquivo baseada no formato."""
        return self.formato
    
    def is_applicable_to(self, orgao=None, modalidade=None, uf=None):
        """Verifica se o template é aplicável ao contexto."""
        if self.orgao_aplicavel and orgao and self.orgao_aplicavel != orgao:
            return False
        if self.modalidade_aplicavel and modalidade and self.modalidade_aplicavel != modalidade:
            return False
        if self.uf_aplicavel and uf and self.uf_aplicavel != uf:
            return False
        return True

class GeracaoDoc(models.Model):
    """Modelo para controle de geração de documentos."""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('processando', 'Processando'),
        ('concluido', 'Concluído'),
        ('erro', 'Erro'),
        ('cancelado', 'Cancelado'),
    ]
    
    tenant = models.ForeignKey('tenancy.Tenant', on_delete=models.CASCADE, related_name='geracoes_doc')
    oportunidade = models.ForeignKey(
        'oportunidades.OportunidadeTenant',
        on_delete=models.CASCADE,
        related_name='geracoes_doc'
    )
    template = models.ForeignKey(TemplateDoc, on_delete=models.CASCADE, related_name='geracoes')
    
    # Status e controle
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pendente')
    progresso = models.IntegerField('Progresso (%)', default=0)
    
    # Dados de entrada
    dados_entrada = models.JSONField('Dados de Entrada', default=dict)
    parametros = models.JSONField('Parâmetros de Geração', default=dict)
    
    # Artefatos gerados
    artefatos = models.JSONField('Artefatos Gerados', default=dict, blank=True)
    # Estrutura: {
    #   'xlsx': {'arquivo': 'path/to/file.xlsx', 'tamanho': 1024, 'hash': 'abc123'},
    #   'pdf': {'arquivo': 'path/to/file.pdf', 'tamanho': 2048, 'hash': 'def456'},
    #   'docx': {'arquivo': 'path/to/file.docx', 'tamanho': 1536, 'hash': 'ghi789'}
    # }
    
    # Logs e erros
    logs = models.JSONField('Logs de Geração', default=list, blank=True)
    erros = models.JSONField('Erros de Geração', default=list, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    iniciado_at = models.DateTimeField('Iniciado em', null=True, blank=True)
    concluido_at = models.DateTimeField('Concluído em', null=True, blank=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='geracoes_criadas'
    )
    
    class Meta:
        verbose_name = 'Geração de Documento'
        verbose_name_plural = 'Gerações de Documentos'
        db_table = 'documentos_geracao_doc'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['oportunidade', 'template']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Geração {self.id} - {self.template.nome} - {self.oportunidade}"
    
    @property
    def is_completed(self):
        """Verifica se a geração foi concluída."""
        return self.status == 'concluido'
    
    @property
    def has_errors(self):
        """Verifica se há erros na geração."""
        return self.status == 'erro' or bool(self.erros)
    
    @property
    def arquivos_gerados(self):
        """Retorna lista de arquivos gerados."""
        if not self.artefatos:
            return []
        return [artefato['arquivo'] for artefato in self.artefatos.values()]
    
    def iniciar_processamento(self):
        """Marca geração como iniciada."""
        self.status = 'processando'
        self.iniciado_at = timezone.now()
        self.save(update_fields=['status', 'iniciado_at'])
    
    def concluir_processamento(self, artefatos=None):
        """Marca geração como concluída."""
        self.status = 'concluido'
        self.progresso = 100
        self.concluido_at = timezone.now()
        if artefatos:
            self.artefatos = artefatos
        self.save(update_fields=['status', 'progresso', 'concluido_at', 'artefatos'])
    
    def registrar_erro(self, erro):
        """Registra erro na geração."""
        self.status = 'erro'
        if not self.erros:
            self.erros = []
        self.erros.append({
            'timestamp': timezone.now().isoformat(),
            'erro': str(erro)
        })
        self.save(update_fields=['status', 'erros'])
    
    def adicionar_log(self, mensagem, nivel='info'):
        """Adiciona log à geração."""
        if not self.logs:
            self.logs = []
        self.logs.append({
            'timestamp': timezone.now().isoformat(),
            'nivel': nivel,
            'mensagem': mensagem
        })
        self.save(update_fields=['logs'])

class DocumentoGerado(models.Model):
    """Modelo para documentos gerados."""
    
    geracao = models.ForeignKey(GeracaoDoc, on_delete=models.CASCADE, related_name='documentos')
    
    # Identificação
    nome = models.CharField('Nome do Documento', max_length=200)
    tipo_arquivo = models.CharField('Tipo de Arquivo', max_length=10)
    
    # Arquivo
    arquivo = models.FileField('Arquivo', upload_to='documentos/gerados/')
    tamanho_bytes = models.BigIntegerField('Tamanho (bytes)', null=True, blank=True)
    hash_arquivo = models.CharField('Hash do Arquivo', max_length=64, blank=True)
    
    # Metadados
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Documento Gerado'
        verbose_name_plural = 'Documentos Gerados'
        db_table = 'documentos_documento_gerado'
        indexes = [
            models.Index(fields=['geracao', 'tipo_arquivo']),
            models.Index(fields=['hash_arquivo']),
        ]
    
    def __str__(self):
        return f"{self.nome} ({self.tipo_arquivo})"
    
    def save(self, *args, **kwargs):
        """Calcula tamanho do arquivo automaticamente."""
        if self.arquivo and not self.tamanho_bytes:
            try:
                self.tamanho_bytes = self.arquivo.size
            except (OSError, IOError):
                pass
        super().save(*args, **kwargs)
