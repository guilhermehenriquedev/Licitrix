"""
Serviço de IA para parsing de editais.
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

import openai
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class EditalAIParser:
    """Parser de editais usando IA."""
    
    def __init__(self):
        """Inicializa o parser."""
        self.openai_client = None
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.openai_client = openai.OpenAI()
        
        # Prompts base para diferentes tipos de extração
        self.prompts = {
            'metadados': """
            Você é um assistente jurídico-operacional especializado em editais brasileiros.
            Extraia apenas os campos solicitados no schema abaixo. Não invente valores.
            Trate números com separador decimal brasileiro (vírgula).
            Retorne JSON válido.
            
            Schema:
            {
                "numero": "string",
                "ano": "integer",
                "objeto": "string",
                "orgao": "string",
                "uf": "string",
                "municipio": "string",
                "modalidade": "string",
                "valor_estimado": "decimal ou null",
                "data_publicacao": "YYYY-MM-DD",
                "data_abertura": "YYYY-MM-DD",
                "data_encerramento": "YYYY-MM-DD ou null",
                "observacoes": "string ou null"
            }
            """,
            
            'itens': """
            Extraia os itens da licitação. Para cada item, retorne:
            {
                "codigo": "string",
                "descricao": "string",
                "quantidade": "decimal",
                "unidade": "string",
                "valor_unitario_estimado": "decimal ou null",
                "categoria": "string ou null",
                "subcategoria": "string ou null"
            }
            """,
            
            'documentos': """
            Extraia os documentos exigidos. Para cada documento, retorne:
            {
                "nome": "string",
                "tipo": "string",
                "descricao": "string ou null",
                "obrigatorio": "boolean"
            }
            """
        }
    
    def parse_edital(self, arquivo_path: str) -> Dict[str, Any]:
        """
        Processa um edital e extrai informações usando IA.
        
        Args:
            arquivo_path: Caminho para o arquivo do edital
            
        Returns:
            Dict com resultado do processamento
        """
        try:
            logger.info(f"Iniciando parsing do edital: {arquivo_path}")
            
            # Lê o conteúdo do arquivo
            conteudo = self._ler_arquivo(arquivo_path)
            if not conteudo:
                return {
                    'sucesso': False,
                    'erros': ['Não foi possível ler o arquivo']
                }
            
            # Extrai metadados básicos
            metadados = self._extrair_metadados(conteudo)
            if not metadados:
                return {
                    'sucesso': False,
                    'erros': ['Não foi possível extrair metadados']
                }
            
            # Extrai itens
            itens = self._extrair_itens(conteudo)
            
            # Extrai documentos exigidos
            documentos = self._extrair_documentos(conteudo)
            
            # Calcula score de confiança
            confidence_score = self._calcular_confidence_score(metadados, itens, documentos)
            
            resultado = {
                'sucesso': True,
                'dados': metadados,
                'itens': itens,
                'documentos': documentos,
                'confidence_score': confidence_score,
                'timestamp': timezone.now().isoformat()
            }
            
            logger.info(f"Parsing concluído com sucesso. Score: {confidence_score}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro no parsing do edital: {e}")
            return {
                'sucesso': False,
                'erros': [str(e)]
            }
    
    def _ler_arquivo(self, arquivo_path: str) -> Optional[str]:
        """Lê o conteúdo do arquivo."""
        try:
            path = Path(arquivo_path)
            
            if path.suffix.lower() == '.pdf':
                return self._ler_pdf(arquivo_path)
            elif path.suffix.lower() in ['.docx', '.doc']:
                return self._ler_docx(arquivo_path)
            elif path.suffix.lower() == '.txt':
                return self._ler_txt(arquivo_path)
            else:
                logger.warning(f"Formato de arquivo não suportado: {path.suffix}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao ler arquivo {arquivo_path}: {e}")
            return None
    
    def _ler_pdf(self, arquivo_path: str) -> Optional[str]:
        """Lê arquivo PDF."""
        try:
            import pdfplumber
            
            texto = ""
            with pdfplumber.open(arquivo_path) as pdf:
                for pagina in pdf.pages:
                    texto += pagina.extract_text() or ""
            
            return texto
            
        except ImportError:
            logger.error("pdfplumber não está instalado")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler PDF {arquivo_path}: {e}")
            return None
    
    def _ler_docx(self, arquivo_path: str) -> Optional[str]:
        """Lê arquivo DOCX."""
        try:
            from docx import Document
            
            doc = Document(arquivo_path)
            texto = ""
            for paragrafo in doc.paragraphs:
                texto += paragrafo.text + "\n"
            
            return texto
            
        except ImportError:
            logger.error("python-docx não está instalado")
            return None
        except Exception as e:
            logger.error(f"Erro ao ler DOCX {arquivo_path}: {e}")
            return None
    
    def _ler_txt(self, arquivo_path: str) -> Optional[str]:
        """Lê arquivo de texto."""
        try:
            with open(arquivo_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Erro ao ler TXT {arquivo_path}: {e}")
            return None
    
    def _extrair_metadados(self, conteudo: str) -> Optional[Dict[str, Any]]:
        """Extrai metadados usando IA."""
        if not self.openai_client:
            return self._extrair_metadados_fallback(conteudo)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['metadados']},
                    {"role": "user", "content": f"Extraia os metadados deste edital:\n\n{conteudo[:4000]}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            resposta = response.choices[0].message.content
            return json.loads(resposta)
            
        except Exception as e:
            logger.error(f"Erro na extração com IA: {e}")
            return self._extrair_metadados_fallback(conteudo)
    
    def _extrair_metadados_fallback(self, conteudo: str) -> Dict[str, Any]:
        """Extrai metadados usando regex como fallback."""
        metadados = {}
        
        # Padrões comuns em editais
        padroes = {
            'numero': r'(?:edital|licitação|pregão)\s*(?:n[oº]\.?\s*)?([A-Z0-9\-/]+)',
            'ano': r'(?:20\d{2})',
            'orgao': r'(?:órgão|entidade|prefeitura|câmara|secretaria)\s*:?\s*([^,\n]+)',
            'uf': r'\b([A-Z]{2})\b',
            'municipio': r'(?:município|cidade)\s*:?\s*([^,\n]+)',
            'modalidade': r'(?:pregão|concorrência|tomada|convite|concurso|leilão)',
            'valor': r'(?:valor|preço|orçamento)\s*:?\s*R?\$?\s*([\d.,]+)',
        }
        
        for campo, padrao in padroes.items():
            match = re.search(padrao, conteudo, re.IGNORECASE)
            if match:
                metadados[campo] = match.group(1).strip()
        
        # Valores padrão
        metadados.update({
            'ano': int(metadados.get('ano', timezone.now().year)),
            'data_publicacao': timezone.now().date().isoformat(),
            'data_abertura': timezone.now().date().isoformat(),
            'data_encerramento': None,
            'observacoes': None
        })
        
        return metadados
    
    def _extrair_itens(self, conteudo: str) -> List[Dict[str, Any]]:
        """Extrai itens da licitação."""
        if not self.openai_client:
            return self._extrair_itens_fallback(conteudo)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['itens']},
                    {"role": "user", "content": f"Extraia os itens desta licitação:\n\n{conteudo[:4000]}"}
                ],
                temperature=0.1,
                max_tokens=1500
            )
            
            resposta = response.choices[0].message.content
            return json.loads(resposta)
            
        except Exception as e:
            logger.error(f"Erro na extração de itens com IA: {e}")
            return self._extrair_itens_fallback(conteudo)
    
    def _extrair_itens_fallback(self, conteudo: str) -> List[Dict[str, Any]]:
        """Extrai itens usando regex como fallback."""
        itens = []
        
        # Padrão básico para itens
        padrao_item = r'(?:item|lote)\s*(\d+)[:.]?\s*([^:]+?)(?:\s*quantidade\s*:?\s*([\d.,]+)\s*([^\s]+))?'
        
        matches = re.finditer(padrao_item, conteudo, re.IGNORECASE)
        
        for match in matches:
            item = {
                'codigo': match.group(1),
                'descricao': match.group(2).strip(),
                'quantidade': float(match.group(3).replace(',', '.')) if match.group(3) else 1.0,
                'unidade': match.group(4) if match.group(4) else 'unidade',
                'valor_unitario_estimado': None,
                'categoria': None,
                'subcategoria': None
            }
            itens.append(item)
        
        return itens
    
    def _extrair_documentos(self, conteudo: str) -> List[Dict[str, Any]]:
        """Extrai documentos exigidos."""
        if not self.openai_client:
            return self._extrair_documentos_fallback(conteudo)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompts['documentos']},
                    {"role": "user", "content": f"Extraia os documentos exigidos:\n\n{conteudo[:4000]}"}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            resposta = response.choices[0].message.content
            return json.loads(resposta)
            
        except Exception as e:
            logger.error(f"Erro na extração de documentos com IA: {e}")
            return self._extrair_documentos_fallback(conteudo)
    
    def _extrair_documentos_fallback(self, conteudo: str) -> List[Dict[str, Any]]:
        """Extrai documentos usando regex como fallback."""
        documentos = []
        
        # Padrões comuns para documentos
        padroes_doc = [
            r'(?:declaração|certificado|contrato|procuração)\s+(?:de\s+)?([^,\n]+)',
            r'(?:documentos?\s+)?(?:exigidos?|necessários?)[:.]?\s*([^:]+)',
        ]
        
        for padrao in padroes_doc:
            matches = re.finditer(padrao, conteudo, re.IGNORECASE)
            for match in matches:
                doc = {
                    'nome': match.group(1).strip(),
                    'tipo': 'declaracao',
                    'descricao': None,
                    'obrigatorio': True
                }
                documentos.append(doc)
        
        return documentos
    
    def _calcular_confidence_score(self, metadados: Dict, itens: List, documentos: List) -> float:
        """Calcula score de confiança da extração."""
        score = 0.0
        
        # Pontua por campos preenchidos
        campos_obrigatorios = ['numero', 'orgao', 'objeto', 'modalidade']
        for campo in campos_obrigatorios:
            if metadados.get(campo):
                score += 0.2
        
        # Pontua por itens extraídos
        if itens:
            score += min(len(itens) * 0.1, 0.3)
        
        # Pontua por documentos extraídos
        if documentos:
            score += min(len(documentos) * 0.05, 0.2)
        
        # Pontua por qualidade dos dados
        if metadados.get('valor_estimado'):
            score += 0.1
        
        if metadados.get('data_publicacao') and metadados.get('data_abertura'):
            score += 0.1
        
        return min(score, 1.0)
