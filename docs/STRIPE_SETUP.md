# Configuração do Stripe para Licitrix

Este documento explica como configurar o Stripe para o sistema de assinaturas do Licitrix.

## 1. Criar Conta no Stripe

1. Acesse [stripe.com](https://stripe.com) e crie uma conta
2. Complete a verificação da conta (dados pessoais e bancários)
3. Ative o modo de teste (Test Mode) para desenvolvimento

## 2. Configurar Produto e Preço

### 2.1 Criar Produto
1. No Dashboard do Stripe, vá para **Products** → **Add Product**
2. Configure o produto:
   - **Name**: Plano Mensal Licitrix
   - **Description**: Acesso completo à plataforma de licitações
   - **Images**: Logo da empresa (opcional)

### 2.2 Criar Preço
1. No produto criado, clique em **Add Price**
2. Configure o preço:
   - **Pricing model**: Standard pricing
   - **Price**: R$ 59,90
   - **Billing period**: Monthly
   - **Currency**: BRL (Real brasileiro)
   - **Billing behavior**: Charge immediately
   - **Trial period**: 0 days (já temos teste de 7 dias na aplicação)

## 3. Configurar Webhooks

### 3.1 Criar Webhook
1. No Dashboard do Stripe, vá para **Developers** → **Webhooks**
2. Clique em **Add endpoint**
3. Configure o endpoint:
   - **Endpoint URL**: `https://seudominio.com/api/users/subscription/webhook/`
   - **Events to send**: Selecione os seguintes eventos:
     - `checkout.session.completed`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
     - `customer.subscription.deleted`
     - `customer.subscription.updated`

### 3.2 Obter Webhook Secret
1. Após criar o webhook, clique nele para ver os detalhes
2. Copie o **Signing secret** (começa com `whsec_`)

## 4. Configurar Variáveis de Ambiente

### 4.1 Backend (.env)
```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID=price_...

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 4.2 Frontend (.env.local)
```bash
# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_STRIPE_PRICE_ID=price_...

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 5. Testar a Integração

### 5.1 Cartões de Teste
Use estes cartões para testar:
- **Sucesso**: `4242 4242 4242 4242`
- **Falha**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`

### 5.2 Fluxo de Teste
1. Crie uma conta de usuário
2. Faça login e acesse o dashboard
3. Clique em "Fazer Upgrade" na página de assinatura
4. Complete o checkout com cartão de teste
5. Verifique se a assinatura foi ativada

## 6. Produção

### 6.1 Ativar Modo Live
1. No Dashboard do Stripe, desative o modo de teste
2. Atualize as variáveis de ambiente com as chaves de produção
3. Configure webhooks para o domínio de produção

### 6.2 Configurações de Segurança
1. Configure **3D Secure** para cartões brasileiros
2. Ative **Radar** para detecção de fraudes
3. Configure **IP allowlist** para webhooks (opcional)

## 7. Monitoramento

### 7.1 Dashboard do Stripe
- **Payments**: Acompanhe pagamentos e falhas
- **Subscriptions**: Gerencie assinaturas ativas
- **Customers**: Visualize base de clientes
- **Webhooks**: Monitore eventos e falhas

### 7.2 Logs da Aplicação
- Verifique logs de webhook no backend
- Monitore erros de pagamento
- Acompanhe criação de assinaturas

## 8. Troubleshooting

### 8.1 Webhook não recebido
- Verifique se a URL está correta
- Confirme se o endpoint está acessível
- Verifique logs de erro no backend

### 8.2 Pagamento falhando
- Confirme se as chaves estão corretas
- Verifique se o preço ID está correto
- Teste com cartões de teste diferentes

### 8.3 Assinatura não ativada
- Verifique logs do webhook
- Confirme se o evento `checkout.session.completed` foi recebido
- Verifique se o usuário foi encontrado no banco

## 9. Recursos Adicionais

- [Documentação oficial do Stripe](https://stripe.com/docs)
- [Stripe CLI para desenvolvimento](https://stripe.com/docs/stripe-cli)
- [Biblioteca Python do Stripe](https://stripe.com/docs/api/python)
- [Biblioteca JavaScript do Stripe](https://stripe.com/docs/js)

## 10. Suporte

Para problemas específicos:
1. Verifique os logs da aplicação
2. Consulte a documentação do Stripe
3. Entre em contato com o suporte do Stripe
4. Abra uma issue no repositório do projeto
