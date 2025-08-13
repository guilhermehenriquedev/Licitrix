"""
Tasks do Celery para o módulo de oportunidades.
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.conf import settings

from .models import Edital, OportunidadeTenant
from .services.ai_parser import EditalAIParser
from .services.oportunidade_matcher import OportunidadeMatcher

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def processar_edital_task(self, edital_id):
    """
    Task para processar um edital com IA.
    """
    try:
        edital = Edital.objects.get(id=edital_id)
        logger.info(f"Iniciando processamento do edital {edital.numero}")
        
        # Marca como processando
        edital.status_ingestao = 'processando'
        edital.save(update_fields=['status_ingestao'])
        
        # Inicializa parser de IA
        parser = EditalAIParser()
        
        # Processa o edital
        resultado = parser.parse_edital(edital.arquivo_original.path)
        
        if resultado['sucesso']:
            # Atualiza edital com dados processados
            edital.arquivo_processado = resultado['dados']
            edital.itens_extraidos = resultado['itens']
            edital.documentos_exigidos = resultado['documentos']
            edital.confidence_score = resultado['confidence_score']
            edital.mark_as_processed()
            
            logger.info(f"Edital {edital.numero} processado com sucesso")
            
            # Dispara task para criar oportunidades para todos os tenants
            criar_oportunidades_para_tenants.delay(edital_id)
            
        else:
            # Registra erros
            edital.parse_errors = resultado['erros']
            edital.status_ingestao = 'erro'
            edital.save(update_fields=['parse_errors', 'status_ingestao'])
            
            logger.error(f"Erro ao processar edital {edital.numero}: {resultado['erros']}")
            
    except Edital.DoesNotExist:
        logger.error(f"Edital {edital_id} não encontrado")
    except Exception as exc:
        logger.error(f"Erro inesperado ao processar edital {edital_id}: {exc}")
        
        # Retry com backoff exponencial
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
        else:
            # Marca como erro após todas as tentativas
            try:
                edital = Edital.objects.get(id=edital_id)
                edital.status_ingestao = 'erro'
                edital.parse_errors = [str(exc)]
                edital.save(update_fields=['status_ingestao', 'parse_errors'])
            except Edital.DoesNotExist:
                pass

@shared_task
def criar_oportunidades_para_tenants(edital_id):
    """
    Cria oportunidades para todos os tenants ativos baseado no edital.
    """
    try:
        edital = Edital.objects.get(id=edital_id)
        logger.info(f"Criando oportunidades para edital {edital.numero}")
        
        # Importa aqui para evitar circular imports
        from core.tenancy.models import Tenant
        
        # Busca todos os tenants ativos
        tenants = Tenant.objects.filter(is_active=True, billing_status='active')
        
        matcher = OportunidadeMatcher()
        
        for tenant in tenants:
            try:
                # Calcula score de match
                match_score = matcher.calcular_match_score(edital, tenant)
                
                # Cria oportunidade se score for relevante
                if match_score >= 0.3:  # Threshold configurável
                    oportunidade, created = OportunidadeTenant.objects.get_or_create(
                        tenant=tenant,
                        edital=edital,
                        defaults={
                            'match_score': match_score,
                            'status': 'nova'
                        }
                    )
                    
                    if created:
                        logger.info(f"Oportunidade criada para tenant {tenant.name} (score: {match_score})")
                    else:
                        # Atualiza score existente
                        oportunidade.match_score = match_score
                        oportunidade.save(update_fields=['match_score'])
                        
            except Exception as e:
                logger.error(f"Erro ao criar oportunidade para tenant {tenant.name}: {e}")
                continue
                
    except Edital.DoesNotExist:
        logger.error(f"Edital {edital_id} não encontrado")
    except Exception as exc:
        logger.error(f"Erro ao criar oportunidades: {exc}")

@shared_task
def processar_editais_pendentes():
    """
    Task agendada para processar editais pendentes.
    """
    try:
        # Busca editais pendentes
        editais_pendentes = Edital.objects.filter(
            status_ingestao='pendente'
        ).order_by('created_at')[:10]  # Processa até 10 por vez
        
        for edital in editais_pendentes:
            processar_edital_task.delay(edital.id)
            
        logger.info(f"Disparadas {editais_pendentes.count()} tasks de processamento")
        
    except Exception as exc:
        logger.error(f"Erro ao processar editais pendentes: {exc}")

@shared_task
def limpar_editais_antigos():
    """
    Remove editais antigos (mais de 2 anos) para economizar espaço.
    """
    try:
        data_limite = timezone.now().date() - timezone.timedelta(days=730)
        
        editais_antigos = Edital.objects.filter(
            data_publicacao__lt=data_limite,
            status_ingestao__in=['concluido', 'erro']
        )
        
        count = editais_antigos.count()
        editais_antigos.delete()
        
        logger.info(f"Removidos {count} editais antigos")
        
    except Exception as exc:
        logger.error(f"Erro ao limpar editais antigos: {exc}")

@shared_task
def atualizar_scores_oportunidades():
    """
    Atualiza scores de match das oportunidades existentes.
    """
    try:
        # Importa aqui para evitar circular imports
        from core.tenancy.models import Tenant
        
        matcher = OportunidadeMatcher()
        
        # Busca oportunidades ativas
        oportunidades = OportunidadeTenant.objects.filter(
            status__in=['nova', 'analisando']
        ).select_related('edital', 'tenant')
        
        for oportunidade in oportunidades:
            try:
                novo_score = matcher.calcular_match_score(oportunidade.edital, oportunidade.tenant)
                oportunidade.match_score = novo_score
                oportunidade.save(update_fields=['match_score'])
                
            except Exception as e:
                logger.error(f"Erro ao atualizar score da oportunidade {oportunidade.id}: {e}")
                continue
                
        logger.info(f"Atualizados scores de {oportunidades.count()} oportunidades")
        
    except Exception as exc:
        logger.error(f"Erro ao atualizar scores de oportunidades: {exc}")
