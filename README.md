# Licitrix - SaaS de Licitações End-to-End

Sistema completo para gestão de licitações públicas com IA, incluindo **sistema de autenticação com período de teste gratuito de 7 dias** e **sistema de billing completo** com integração Stripe para assinaturas recorrentes.

## 🚀 Quick Start (5 minutos)

### Pré-requisitos
- Docker e Docker Compose
- Git

### 1. Clone e Execute
```bash
git clone <repository-url>
cd Licitrix
make run
```

### 2. Acesse a Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

### 3. Credenciais de Teste
- **Superadmin**: `admin@licitrix.com` / `admin123`
- **Usuário Demo**: `demo@licitrix.com` / `demo123`

---

# 📖 **Licitrix — Guia de Execução Local**

## 1. Visão Geral

Este guia fornece instruções completas para executar o Licitrix localmente, incluindo:
- **Backend**: Django + DRF + Celery + Redis
- **Frontend**: Next.js + Material-UI
- **Banco**: PostgreSQL
- **Pagamentos**: Stripe (Checkout + Webhooks)
- **Cache/Filas**: Redis

## 2. Pré-requisitos

### Com Docker (Recomendado)
- Docker Desktop 20.10+
- Docker Compose 2.0+
- Git
- Editor de código (VS Code, IntelliJ, etc.)

### Sem Docker (Dev Nativo)
- Python 3.12+
- Node.js 18+ (LTS)
- PostgreSQL 16+
- Redis 7+
- Git
- Editor de código

## 3. Variáveis de Ambiente

### Backend (.env)
```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Banco de Dados
POSTGRES_DB=licitrix
POSTGRES_USER=licitrix
POSTGRES_PASSWORD=licitrix
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe (obrigatório para billing)
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Configurações de Billing
STRIPE_GRACE_PERIOD_DAYS=3
STRIPE_TRIAL_DAYS=7
STRIPE_MONTHLY_PRICE=59.90

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Frontend (.env.local)
```bash
# Next.js
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_STRIPE_PRICE_ID=price_...
```

## 4. Executando com Docker (Recomendado)

### 4.1 Clone e Setup
```bash
# Clone o repositório
git clone <repository-url>
cd Licitrix

# Copie as variáveis de ambiente
cp .env.example .env
cp apps/web/.env.local.example apps/web/.env.local

# Edite as variáveis (especialmente Stripe)
nano .env
nano apps/web/.env.local
```

### 4.2 Configurar Stripe (Obrigatório)
```bash
# 1. Acesse https://dashboard.stripe.com
# 2. Crie um produto "Plano Mensal Licitrix"
# 3. Configure preço R$ 59,90/mês (BRL)
# 4. Copie as chaves para .env
# 5. Configure webhook endpoint: http://localhost:8000/api/users/subscription/webhook/
# 6. Copie webhook secret para .env
```

### 4.3 Executar Aplicação
```bash
# Construir e executar todos os serviços
make run

# Ou manualmente:
docker compose up --build -d

# Verificar status
make status

# Ver logs
make logs
```

### 4.4 Setup Inicial
```bash
# Executar migrações
make migrate

# Criar superusuário
make createsuperuser

# Carregar dados de exemplo
make seed

# Verificar saúde dos serviços
make health
```

### 4.5 Acessar Aplicação
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/
- **Redis Commander**: http://localhost:8081
- **MailHog**: http://localhost:8025

## 5. Executando sem Docker (Modo Dev Nativo)

### 5.1 Setup do Backend
```bash
# Navegar para o backend
cd apps/backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Carregar dados de exemplo
python manage.py loaddata seed.json

# Executar servidor
python manage.py runserver
```

### 5.2 Setup do Frontend
```bash
# Navegar para o frontend
cd apps/web

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.local.example .env.local
# Editar .env.local com suas configurações

# Executar em modo desenvolvimento
npm run dev
```

### 5.3 Setup dos Serviços Auxiliares
```bash
# PostgreSQL
# Instalar PostgreSQL 16+
# Criar banco 'licitrix'
# Criar usuário 'licitrix' com senha 'licitrix'

# Redis
# Instalar Redis 7+
# Executar: redis-server

# Celery (em terminal separado)
cd apps/backend
celery -A core worker -l info

# Celery Beat (em terminal separado)
cd apps/backend
celery -A core beat -l info
```

## 6. Stripe — Checkout & Webhooks

### 6.1 Configuração no Dashboard
1. **Produto**: "Plano Mensal Licitrix"
2. **Preço**: R$ 59,90/mês (BRL)
3. **Webhook**: `http://localhost:8000/api/users/subscription/webhook/`
4. **Eventos**: Todos os eventos de billing

### 6.2 Testar Webhooks Localmente
```bash
# Instalar Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login no Stripe
stripe login

# Escutar webhooks
stripe listen --forward-to localhost:8000/api/users/subscription/webhook/

# Copiar webhook secret para .env
```

### 6.3 Cartões de Teste
- **Sucesso**: `4242 4242 4242 4242`
- **Falha**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`
- **Expiração**: `4000 0000 0000 0069`

## 7. Seeds, Usuário Admin e Dados de Exemplo

### 7.1 Usuários Padrão
```bash
# Superadmin
Email: admin@licitrix.com
Senha: admin123

# Usuário Demo
Email: demo@licitrix.com
Senha: demo123
```

### 7.2 Carregar Dados
```bash
# Com Docker
make seed

# Sem Docker
python manage.py loaddata seed.json
```

### 7.3 Criar Superusuário
```bash
# Com Docker
make createsuperuser

# Sem Docker
python manage.py createsuperuser
```

## 8. Testes, Lint e Formatação

### 8.1 Testes
```bash
# Executar todos os testes
make test

# Testes específicos
make test-backend
make test-frontend

# Com Docker
docker compose exec api pytest
docker compose exec web npm test
```

### 8.2 Lint e Formatação
```bash
# Backend
make lint-backend
make format-backend

# Frontend
make lint-frontend
make format-frontend

# Tudo
make lint
make format
```

### 8.3 Verificação de Qualidade
```bash
# Verificar cobertura
make coverage

# Verificar segurança
make security

# Verificar dependências
make deps-check
```

## 9. Comandos Úteis (Makefile)

### 9.1 Desenvolvimento
```bash
make run          # Executar aplicação
make stop         # Parar aplicação
make restart      # Reiniciar aplicação
make logs         # Ver logs
make status       # Status dos serviços
```

### 9.2 Banco de Dados
```bash
make migrate      # Executar migrações
make makemigrations  # Criar migrações
make reset-db     # Resetar banco
make backup       # Backup do banco
make restore      # Restaurar backup
```

### 9.3 Usuários e Dados
```bash
make seed         # Carregar dados de exemplo
make createsuperuser  # Criar superusuário
make shell        # Shell Django
make dbshell      # Shell do banco
```

### 9.4 Manutenção
```bash
make clean        # Limpar arquivos temporários
make rebuild      # Reconstruir containers
make update       # Atualizar dependências
make health       # Verificar saúde dos serviços
```

## 10. Solução de Problemas

### 10.1 Problemas Comuns

#### Backend não inicia
```bash
# Verificar logs
make logs

# Verificar variáveis de ambiente
cat .env

# Verificar banco
make status

# Resetar banco
make reset-db
```

#### Frontend não carrega
```bash
# Verificar API
curl http://localhost:8000/health/

# Verificar variáveis
cat apps/web/.env.local

# Limpar cache
cd apps/web && npm run clean
```

#### Stripe não funciona
```bash
# Verificar chaves
cat .env | grep STRIPE

# Testar webhook
stripe listen --forward-to localhost:8000/api/users/subscription/webhook/

# Verificar logs do webhook
make logs
```

### 10.2 Logs e Debug
```bash
# Logs em tempo real
make logs-follow

# Logs específicos
docker compose logs api
docker compose logs web
docker compose logs db

# Shell de debug
make shell
make dbshell
```

### 10.3 Reset Completo
```bash
# Parar tudo
make stop

# Remover volumes
docker compose down -v

# Reconstruir
make rebuild

# Executar
make run
```

---

## 🔐 Sistema de Autenticação e Billing

### Funcionalidades
- ✅ **Cadastro** com período de teste gratuito de 7 dias
- ✅ **Login/Logout** com JWT
- ✅ **Recuperação de senha** por email
- ✅ **Verificação de acesso** baseada em assinatura
- ✅ **Integração Stripe** para pagamentos recorrentes
- ✅ **Autogestão** via Stripe Customer Portal
- ✅ **Sistema de dunning** com grace period de 3 dias
- ✅ **Cancelamento flexível** (imediato ou fim do período)
- ✅ **Reativação** de assinaturas canceladas

### Fluxo do Usuário
1. **Cadastro** → Início automático do teste gratuito (7 dias)
2. **Login** → Acesso total a todas as funcionalidades
3. **Fim do teste** → Redirecionamento para página de assinatura
4. **Pagamento Stripe** → Acesso liberado (R$ 59,90/mês)
5. **Autogestão** → Portal do cliente para gerenciar pagamentos
6. **Cobrança automática** → Renovação mensal via Stripe

### Sistema de Dunning
- **Grace period**: 3 dias de acesso após falha de pagamento
- **Retentativas automáticas**: Configuradas no Stripe
- **Bloqueio progressivo**: Acesso removido após grace period
- **Reativação**: Botão para reativar com novo pagamento

## 🏗️ Arquitetura

### Monorepo
```
Licitrix/
├── apps/
│   ├── backend/          # Django REST API
│   └── web/             # Next.js Frontend
├── packages/
│   └── shared/          # Tipos e utilitários
└── infra/               # Docker, Terraform
```

### Stack Técnica
- **Backend**: Python 3.12, Django 5+, DRF, Celery, Redis, PostgreSQL
- **Frontend**: Next.js 14, React 18, Material-UI, TypeScript
- **IA/ML**: OpenAI/Anthropic, LangChain, Pandas
- **Pagamentos**: Stripe (assinaturas recorrentes + Customer Portal)
- **Infra**: Docker, AWS (ECS, RDS, S3), Terraform

## 📱 Módulos Funcionais

### 1. **Prospecção Inteligente** 🎯
- Cadastro de nicho por empresa (CNAE, UF, modalidades)
- Ingestão de oportunidades (upload de edital + crawler)
- Alertas diários por email/WhatsApp
- Dashboard de novas licitações

### 2. **Precificação com IA** 🤖
- Análise automática de editais
- 3 estratégias: Competitiva / Moderada / Conservadora
- Simulador de cenários e sensibilidade
- Histórico de preços vencedores

### 3. **Geração de Documentos** 📄
- Planilhas de preços (XLSX) conforme edital
- Declarações e documentos (PDF/DOCX)
- Templates parametrizáveis por órgão
- Assinatura digital (preparado para ICP-Brasil)

### 4. **Gestão de Contratos** 📋
- Cronograma e marcos de medição
- Upload de evidências e documentos
- Aceite do fiscal e controle de qualidade
- SLAs e indicadores de performance

### 5. **Financeiro & Cobrança** 💰
- Emissão de NF-e/NFS-e (eNotas/NFE.io)
- DDA, boletos e PIX
- Lembretes automáticos de cobrança
- Relatórios de fluxo de caixa

## 🔒 Segurança & LGPD

- **Autenticação**: JWT + Refresh tokens
- **Autorização**: RBAC granular por tenant
- **LGPD-by-design**: Consentimento, retenção, auditoria
- **Criptografia**: AES-256 em dados sensíveis
- **Auditoria**: Trilhas imutáveis de todas as ações

## 📊 Observabilidade

- **Logs**: Estruturados com contexto
- **Métricas**: Prometheus + Grafana
- **Traces**: OpenTelemetry distribuído
- **Monitoramento**: Sentry para erros
- **Health Checks**: API, banco, Redis

## 📚 Documentação

- [Configuração Stripe](docs/STRIPE_SETUP.md)
- [Sistema de Billing](docs/BILLING_SYSTEM.md)
- [API Documentation](http://localhost:8000/api/docs/)
- [Arquitetura](docs/ARCHITECTURE.md)
- [Deploy](docs/DEPLOY.md)

## 🎯 Status MVP

### ✅ Concluído
- [x] Monorepo estruturado
- [x] Backend Django com modelos completos
- [x] Frontend Next.js com Material-UI
- [x] Sistema de autenticação completo
- [x] Período de teste gratuito (7 dias)
- [x] Integração Stripe para assinaturas
- [x] Middleware de controle de acesso
- [x] **Sistema de billing completo**
- [x] **Stripe Customer Portal**
- [x] **Sistema de dunning com grace period**
- [x] **Cancelamento flexível e reativação**
- [x] **Controle de acesso baseado em status**
- [x] Docker Compose para desenvolvimento
- [x] CI/CD básico com GitHub Actions
- [x] Documentação de configuração

### 🔄 Em Desenvolvimento
- [ ] Telas de oportunidades e precificação
- [ ] Jobs Celery para processamento IA
- [ ] Geração de documentos
- [ ] Sistema de notificações

### 📋 Próximos Passos
- [ ] Implementar módulos funcionais
- [ ] Testes automatizados (≥85% cobertura)
- [ ] Deploy em produção (AWS)
- [ ] Monitoramento e alertas
- [ ] LGPD e compliance

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/username/licitrix/issues)
- **Documentação**: [docs/](docs/)
- **Email**: suporte@licitrix.com

---

**Licitrix** - Transformando a gestão de licitações com IA e automação 🚀
