'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Container,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material'
import {
  CheckCircle,
  Star,
  Security,
  Speed,
  Support,
  CreditCard,
  Timer,
} from '@mui/icons-material'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface UserStatus {
  subscription_status: string
  is_in_trial_period: boolean
  has_active_access: boolean
  days_until_trial_end: number
  days_until_subscription_end: number
}

export default function SubscriptionPage() {
  const [userStatus, setUserStatus] = useState<UserStatus | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isCreatingCheckout, setIsCreatingCheckout] = useState(false)
  const router = useRouter()

  useEffect(() => {
    checkUserStatus()
  }, [])

  const checkUserStatus = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/auth/login')
        return
      }

      const response = await fetch('/api/users/status/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const status = await response.json()
        setUserStatus(status)
      } else {
        toast.error('Erro ao verificar status do usuário')
      }
    } catch (error) {
      toast.error('Erro de conexão')
    }
  }

  const handleSubscribe = async () => {
    setIsCreatingCheckout(true)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/users/subscription/create-checkout-session/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          success_url: `${window.location.origin}/dashboard?subscription=success`,
          cancel_url: `${window.location.origin}/subscription?subscription=cancelled`,
        }),
      })

      const result = await response.json()

      if (response.ok) {
        // Redirecionar para o Stripe Checkout
        window.location.href = result.checkout_url
      } else {
        toast.error(result.error || 'Erro ao criar sessão de checkout')
      }
    } catch (error) {
      toast.error('Erro de conexão')
    } finally {
      setIsCreatingCheckout(false)
    }
  }

  const features = [
    'Acesso completo a todas as funcionalidades',
    'Análise de oportunidades com IA',
    'Precificação inteligente (3 estratégias)',
    'Geração automática de documentos',
    'Gestão de contratos e medições',
    'Sistema de faturamento e cobrança',
    'Suporte prioritário',
    'Atualizações e melhorias contínuas',
  ]

  if (!userStatus) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Escolha seu Plano
          </Typography>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            Continue aproveitando o Licitrix com acesso total
          </Typography>
          
          {userStatus.subscription_status === 'teste' && (
            <Alert severity="info" sx={{ maxWidth: 600, mx: 'auto', mb: 3 }}>
              <Typography variant="body1">
                <strong>⏰ Seu período de teste termina em {userStatus.days_until_trial_end} dia(s)</strong>
                <br />
                Faça upgrade agora para manter acesso ininterrupto à plataforma.
              </Typography>
            </Alert>
          )}
        </Box>

        {/* Plano */}
        <Grid container justifyContent="center">
          <Grid item xs={12} md={8} lg={6}>
            <Card elevation={3} sx={{ position: 'relative' }}>
              {userStatus.subscription_status === 'teste' && (
                <Box
                  sx={{
                    position: 'absolute',
                    top: -12,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    zIndex: 1,
                  }}
                >
                  <Chip
                    label="Recomendado"
                    color="primary"
                    icon={<Star />}
                    sx={{ fontWeight: 'bold' }}
                  />
                </Box>
              )}
              
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ textAlign: 'center', mb: 4 }}>
                  <Typography variant="h4" component="h2" gutterBottom>
                    Plano Mensal
                  </Typography>
                  <Typography variant="h3" component="div" color="primary" gutterBottom>
                    R$ 59,90
                  </Typography>
                  <Typography variant="body1" color="text.secondary">
                    por mês
                  </Typography>
                </Box>

                <Divider sx={{ my: 3 }} />

                <List>
                  {features.map((feature, index) => (
                    <ListItem key={index} sx={{ px: 0 }}>
                      <ListItemIcon sx={{ minWidth: 40 }}>
                        <CheckCircle color="success" />
                      </ListItemIcon>
                      <ListItemText primary={feature} />
                    </ListItem>
                  ))}
                </List>

                <Divider sx={{ my: 3 }} />

                <Box sx={{ textAlign: 'center' }}>
                  <Button
                    variant="contained"
                    size="large"
                    fullWidth
                    onClick={handleSubscribe}
                    disabled={isCreatingCheckout || userStatus.subscription_status === 'ativo'}
                    sx={{ py: 2, fontSize: '1.1rem' }}
                  >
                    {isCreatingCheckout ? (
                      <CircularProgress size={24} color="inherit" />
                    ) : userStatus.subscription_status === 'ativo' ? (
                      'Plano Ativo'
                    ) : (
                      'Assinar Agora'
                    )}
                  </Button>

                  {userStatus.subscription_status === 'ativo' && (
                    <Alert severity="success" sx={{ mt: 2 }}>
                      Você já possui um plano ativo!
                    </Alert>
                  )}

                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    Cancele a qualquer momento • Sem taxas ocultas
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Benefícios */}
        <Box sx={{ mt: 8 }}>
          <Typography variant="h4" component="h2" align="center" gutterBottom>
            Por que escolher o Licitrix?
          </Typography>
          
          <Grid container spacing={4} sx={{ mt: 4 }}>
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Security color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Segurança e LGPD
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sua empresa e dados estão protegidos com as melhores práticas de segurança e conformidade LGPD.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Speed color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Eficiência
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Automatize processos manuais e foque no que realmente importa para seu negócio.
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Box sx={{ textAlign: 'center' }}>
                <Support color="primary" sx={{ fontSize: 60, mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Suporte Especializado
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Nossa equipe está sempre pronta para ajudar você a aproveitar ao máximo a plataforma.
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* FAQ */}
        <Box sx={{ mt: 8 }}>
          <Typography variant="h4" component="h2" align="center" gutterBottom>
            Perguntas Frequentes
          </Typography>
          
          <Grid container spacing={3} sx={{ mt: 4 }}>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Como funciona o período de teste?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Você tem 7 dias de acesso total e gratuito a todas as funcionalidades. Após esse período, 
                  será necessário assinar um plano para continuar usando.
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Posso cancelar a qualquer momento?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Sim! Você pode cancelar sua assinatura a qualquer momento através do painel de controle 
                  ou entrando em contato com nosso suporte.
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  O que acontece se o pagamento falhar?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Em caso de falha no pagamento, você receberá notificações e terá um período de carência 
                  para regularizar a situação antes do bloqueio do acesso.
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Há taxas de setup ou cancelamento?
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Não! Não cobramos taxas de setup, cancelamento ou qualquer outra taxa oculta. 
                  Você paga apenas o valor mensal anunciado.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Box>
      </Box>
    </Container>
  )
}
