"""
Serviço para calcular match entre editais e tenants.
"""

import logging
from typing import List, Dict, Any
from django.db.models import Q

logger = logging.getLogger(__name__)

class OportunidadeMatcher:
    """Calcula score de match entre editais e tenants."""
    
    def calcular_match_score(self, edital, tenant) -> float:
        """Calcula score de relevância da oportunidade para o tenant."""
        score = 0.0
        
        # Match por CNAE (40% do score)
        score += self._calcular_match_cnae(edital, tenant) * 0.4
        
        # Match por localização (30% do score)
        score += self._calcular_match_localizacao(edital, tenant) * 0.3
        
        # Match por palavras-chave (20% do score)
        score += self._calcular_match_keywords(edital, tenant) * 0.2
        
        # Match por valor (10% do score)
        score += self._calcular_match_valor(edital, tenant) * 0.1
        
        return min(score, 1.0)
    
    def _calcular_match_cnae(self, edital, tenant) -> float:
        """Calcula match por CNAE."""
        # Implementação básica - pode ser expandida com IA
        return 0.5  # Score médio por padrão
    
    def _calcular_match_localizacao(self, edital, tenant) -> float:
        """Calcula match por localização."""
        if edital.uf == tenant.uf:
            return 1.0
        elif edital.municipio == tenant.municipio:
            return 0.8
        else:
            return 0.3
    
    def _calcular_match_keywords(self, edital, tenant) -> float:
        """Calcula match por palavras-chave."""
        # Implementação básica
        return 0.6
    
    def _calcular_match_valor(self, edital, tenant) -> float:
        """Calcula match por valor da licitação."""
        if not edital.valor_estimado:
            return 0.5
        
        # Lógica baseada no plano do tenant
        if tenant.plan == 'free' and edital.valor_estimado > 100000:
            return 0.3
        elif tenant.plan == 'basic' and edital.valor_estimado > 500000:
            return 0.5
        else:
            return 0.8
