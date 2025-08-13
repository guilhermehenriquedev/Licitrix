'use client'

import React, { useState, useEffect } from 'react'
import { Box, Container, Typography, Paper, Button, Grid, Card, CardContent, Alert } from '@mui/material'
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

  const handleManageSubscription = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/users/subscription/create-portal-session/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          return_url: `${window.location.origin}/subscription`,
        }),
      })

      const result = await response.json()

      if (response.ok) {
        // Redirecionar para o Stripe Customer Portal
        window.location.href = result.portal_url
      } else {
        toast.error(result.error || 'Erro ao acessar portal do cliente')
      }
    } catch (error) {
      toast.error('Erro de conexão')
    }
  }

  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box textAlign="center">
          <Typography variant="h4">Carregando...</Typography>
        </Box>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        Assinatura Licitrix
      </Typography>

      <Grid container spacing={4}>
        {/* Status do Usuário */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Status da Conta
              </Typography>
              
              {userStatus && (
                <Box>
                  {userStatus.is_in_trial_period ? (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      Período de teste ativo - {userStatus.days_until_trial_end} dias restantes
                    </Alert>
                  ) : userStatus.has_active_access ? (
                    <Alert severity="success" sx={{ mb: 2 }}>
                      Assinatura ativa
                    </Alert>
                  ) : (
                    <Alert severity="warning" sx={{ mb: 2 }}>
                      Sem assinatura ativa
                    </Alert>
                  )}
                  
                  <Typography variant="body1">
                    Status: {userStatus.subscription_status}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Plano */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Plano Mensal
              </Typography>
              
              <Typography variant="h4" color="primary" gutterBottom>
                R$ 59,90/mês
              </Typography>
              
              <Typography variant="body1" paragraph>
                Acesso completo a todas as funcionalidades da plataforma Licitrix
              </Typography>

              {userStatus && !userStatus.has_active_access && (
                <Button
                  variant="contained"
                  color="primary"
                  size="large"
                  fullWidth
                  onClick={handleSubscribe}
                  disabled={isCreatingCheckout}
                  sx={{ mt: 2 }}
                >
                  {isCreatingCheckout ? 'Processando...' : 'Assinar Agora'}
                </Button>
              )}

              {userStatus && userStatus.has_active_access && (
                <Button
                  variant="outlined"
                  color="primary"
                  size="large"
                  fullWidth
                  onClick={handleManageSubscription}
                  sx={{ mt: 2 }}
                >
                  Gerenciar Assinatura
                </Button>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}
