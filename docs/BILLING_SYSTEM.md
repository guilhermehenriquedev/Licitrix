# Sistema de Billing Completo - Licitrix

Este documento descreve o sistema completo de cobrança e assinaturas do Licitrix, incluindo período de teste gratuito, cobrança automática via Stripe, autogestão e sistema de dunning.

## 🎯 **Visão Geral**

O sistema implementa um modelo SaaS completo com:
- **7 dias de teste gratuito** sem cartão obrigatório
- **Cobrança automática mensal** via Stripe (R$ 59,90/mês)
- **Autogestão** via Stripe Customer Portal
- **Sistema de dunning** com grace period de 3 dias
- **Cancelamento flexível** (imediato ou ao fim do período)

## 🔄 **Fluxos Principais**

### 1. **Cadastro e Trial**
```
Usuário se cadastra → Trial de 7 dias inicia automaticamente
→ Acesso total durante o trial
→ Notificações em D-2 e D-0
```

### 2. **Conversão para Assinatura**
```
Trial expira → Redirecionamento para página de assinatura
→ Stripe Checkout → Criação de Customer + Subscription
→ Webhook ativa acesso → Usuário pode usar a plataforma
```

### 3. **Cobrança Recorrente**
```
Stripe fatura mensalmente → Webhook invoice.payment_succeeded
→ Atualiza current_period_end → Acesso mantido
```

### 4. **Falha de Pagamento**
```
Pagamento falha → Webhook invoice.payment_failed
→ Status = past_due → Grace period de 3 dias inicia
→ Acesso mantido durante grace period
→ Após grace period → Acesso bloqueado
```

### 5. **Cancelamento**
```
Usuário cancela → Opção: imediato ou fim do período
→ Stripe atualiza subscription → Webhook atualiza BD
→ Acesso removido conforme escolha
```

## 🏗️ **Arquitetura Técnica**

### **Backend (Django)**
- **Modelos**: `User`, `Subscription`, `Invoice`
- **Serviços**: `StripeService` para operações Stripe
- **Views**: Endpoints para checkout, portal, cancelamento
- **Middleware**: Controle de acesso baseado em status
- **Webhooks**: Processamento de eventos Stripe

### **Frontend (Next.js)**
- **Páginas**: Login, Registro, Assinatura, Dashboard
- **Componentes**: Status de assinatura, ações de billing
- **Hooks**: `useAuth`, `useRequireSubscription`
- **Integração**: Stripe Checkout e Customer Portal

### **Stripe**
- **Produto**: "Plano Mensal Licitrix"
- **Preço**: R$ 59,90/mês (BRL)
- **Webhooks**: Eventos de billing e assinatura
- **Customer Portal**: Autogestão de pagamentos

## 📊 **Modelos de Dados**

### **User**
```python
class User(AbstractUser):
    # Campos básicos
    email, first_name, last_name, role
    
    # Trial
    data_inicio_teste, data_fim_teste
    
    # Assinatura
    plano_ativo, data_inicio_plano, data_fim_plano
    
    # Stripe
    stripe_customer_id, stripe_subscription_id
    
    # Propriedades
    is_in_trial_period, has_active_access, subscription_status
```

### **Subscription**
```python
class Subscription(models.Model):
    # Relacionamentos
    user (OneToOne)
    
    # Stripe
    stripe_customer_id, stripe_subscription_id, stripe_price_id
    
    # Status
    status (trialing, active, past_due, canceled, etc.)
    cancel_at_period_end, canceled_at
    
    # Períodos
    current_period_start, current_period_end
    trial_start, trial_end
    
    # Pagamento
    default_payment_method_*, grace_period_until
    
    # Propriedades
    is_active, is_canceled, has_grace_period
```

### **Invoice**
```python
class Invoice(models.Model):
    # Relacionamentos
    subscription (ForeignKey)
    
    # Stripe
    stripe_invoice_id, stripe_customer_id
    
    # Valores
    status, amount_due, amount_paid, currency
    
    # URLs
    hosted_invoice_url, invoice_pdf
    
    # Datas
    due_date, paid_at, created_at
    
    # Propriedades
    is_paid, is_overdue
```

## 🔌 **Endpoints da API**

### **Autenticação**
- `POST /api/users/auth/register/` - Cadastro
- `POST /api/users/auth/login/` - Login
- `POST /api/users/auth/logout/` - Logout
- `GET /api/users/status/` - Status da assinatura

### **Assinaturas**
- `POST /api/users/subscription/create-checkout-session/` - Checkout
- `POST /api/users/subscription/create-portal-session/` - Portal
- `POST /api/users/subscription/cancel/` - Cancelar
- `POST /api/users/subscription/reactivate/` - Reativar
- `GET /api/users/subscription/invoices/` - Listar faturas

### **Webhooks**
- `POST /api/users/subscription/webhook/` - Eventos Stripe

## 🎮 **Funcionalidades do Usuário**

### **Via Stripe Checkout**
- Criar assinatura com cartão
- Aplicar códigos promocionais
- Processamento seguro de pagamento

### **Via Customer Portal**
- Atualizar método de pagamento
- Ver histórico de faturas
- Baixar faturas em PDF
- Cancelar assinatura
- Reativar assinatura cancelada

### **Via Plataforma**
- Ver status da assinatura
- Cancelar assinatura (imediato/fim período)
- Reativar assinatura
- Acessar faturas

## 🚨 **Sistema de Dunning**

### **Grace Period**
- **Duração**: 3 dias configurável
- **Comportamento**: Acesso mantido
- **Notificações**: Avisos de pagamento em atraso
- **CTA**: Botão para atualizar pagamento

### **Após Grace Period**
- **Acesso**: Bloqueado
- **Status**: `past_due` (sem grace period)
- **Redirecionamento**: Página de assinatura
- **Mensagem**: "Pagamento em atraso. Acesso bloqueado."

### **Retentativas**
- **Stripe**: Configuração automática de retentativas
- **Frequência**: 1, 3, 5, 7 dias após falha
- **Métodos**: Mesmo cartão ou novo método

## 🔒 **Controle de Acesso**

### **Middleware de Verificação**
```python
def _has_active_access(self, user):
    # Trial ativo
    if user.is_in_trial_period:
        return True
    
    # Plano ativo
    if user.plano_ativo:
        return True
    
    # Grace period
    if subscription.has_grace_period:
        return True
    
    # Cancelada mas no período atual
    if subscription.cancel_at_period_end and subscription.current_period_end > now:
        return True
    
    return False
```

### **Status de Acesso**
- **`trial`**: Acesso total (7 dias)
- **`active`**: Acesso total (assinatura ativa)
- **`past_due_grace`**: Acesso total (grace period)
- **`past_due_blocked`**: Acesso bloqueado
- **`canceled_period_end`**: Acesso até fim do período
- **`canceled_expired`**: Acesso bloqueado
- **`no_subscription`**: Acesso bloqueado

## 📧 **Notificações e Emails**

### **Trial**
- **Boas-vindas**: Confirmação de cadastro + 7 dias
- **D-2**: "Seu trial termina em 2 dias"
- **D-0**: "Trial expirado. Faça upgrade agora!"

### **Assinatura**
- **Ativação**: Confirmação de assinatura
- **Renovação**: Fatura paga com sucesso
- **Falha**: Pagamento falhou + grace period
- **Cancelamento**: Confirmação + data efetiva

### **Dunning**
- **Grace period**: Avisos de pagamento em atraso
- **Bloqueio**: Acesso bloqueado após grace period
- **Reativação**: Confirmação de pagamento

## 🧪 **Testes e Validação**

### **Cartões de Teste**
- **Sucesso**: `4242 4242 4242 4242`
- **Falha**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`
- **Expiração**: `4000 0000 0000 0069`

### **Cenários de Teste**
1. **Cadastro → Trial → Assinatura**
2. **Pagamento falha → Grace period → Bloqueio**
3. **Cancelamento fim período → Reativação**
4. **Cancelamento imediato → Nova assinatura**
5. **Atualização método de pagamento**

## 📈 **Métricas e Monitoramento**

### **KPIs de Billing**
- **Conversão trial → pago**: % de usuários que assinam
- **Churn rate**: % de cancelamentos mensais
- **MRR**: Monthly Recurring Revenue
- **ARPA**: Average Revenue Per Account
- **Grace period usage**: % de usuários em grace period

### **Alertas**
- **Webhook falha**: Eventos não processados
- **Pagamentos repetidos falhando**: Risco de churn
- **Discrepâncias Stripe ↔ BD**: Sincronização
- **Grace period expirando**: Usuários para bloquear

## 🔧 **Configuração e Deploy**

### **Variáveis de Ambiente**
```bash
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Billing
STRIPE_GRACE_PERIOD_DAYS=3
STRIPE_TRIAL_DAYS=7
STRIPE_MONTHLY_PRICE=59.90

# URLs
FRONTEND_URL=http://localhost:3000
```

### **Webhooks Stripe**
- **Endpoint**: `/api/users/subscription/webhook/`
- **Eventos**: Todos os eventos de billing
- **Segurança**: Validação de assinatura
- **Retry**: Configuração automática do Stripe

### **Deploy**
1. **Configurar Stripe** (produto, preço, webhooks)
2. **Atualizar variáveis** de ambiente
3. **Executar migrações** do banco
4. **Testar webhooks** com Stripe CLI
5. **Validar fluxos** de assinatura

## 🚀 **Próximos Passos**

### **Melhorias Futuras**
- **Planos múltiplos**: Básico, Pro, Enterprise
- **Cobrança anual**: Desconto para pagamento anual
- **Cupons e promoções**: Sistema de desconto
- **Proratação**: Cálculo de valores parciais
- **Métricas avançadas**: Dashboard de billing

### **Integrações**
- **Zapier**: Automações de billing
- **Slack**: Notificações de pagamento
- **Analytics**: Tracking de conversão
- **CRM**: Sincronização com sistemas externos

---

**Sistema de Billing Licitrix** - Implementação completa e robusta para SaaS de licitações 🚀
