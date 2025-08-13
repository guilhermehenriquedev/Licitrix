'use client'

import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  LinearProgress,
  Paper,
} from '@mui/material'
import {
  TrendingUp,
  Assignment,
  Description,
  Payment,
  Warning,
  CheckCircle,
  Timer,
} from '@mui/icons-material'
import { useRequireAuth, useRequireSubscription } from '../../hooks/useAuth'
import { useRouter } from 'next/navigation'

export default function Dashboard() {
  const { user, isLoading } = useRequireSubscription()
  const router = useRouter()
  const [stats, setStats] = useState({
    oportunidades: 12,
    propostas: 8,
    contratos: 5,
    faturas: 3,
  })

  const [recentOportunidades] = useState([
    {
      id: 1,
      titulo: 'Licitação para Fornecimento de Material de Escritório',
      orgao: 'Prefeitura Municipal',
      valor: 'R$ 45.000,00',
      prazo: '15 dias',
      status: 'Em análise',
    },
    {
      id: 2,
      titulo: 'Aquisição de Equipamentos de Informática',
      orgao: 'Secretaria de Educação',
      valor: 'R$ 120.000,00',
      prazo: '8 dias',
      status: 'Precificando',
    },
    {
      id: 3,
      titulo: 'Serviços de Manutenção Predial',
      orgao: 'Hospital Municipal',
      valor: 'R$ 85.000,00',
      prazo: '22 dias',
      status: 'Documentação',
    },
  ])

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <LinearProgress />
        </Box>
      </Container>
    )
  }

  if (!user) {
    return null
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        {/* Header com status da assinatura */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Dashboard
          </Typography>
          
          {/* Status da assinatura */}
          <Paper sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="h6" gutterBottom>
                  Status da Assinatura
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Chip
                    label={user.subscription_status === 'ativo' ? 'Plano Ativo' : 'Período de Teste'}
                    color={user.subscription_status === 'ativo' ? 'success' : 'warning'}
                    icon={user.subscription_status === 'ativo' ? <CheckCircle /> : <Timer />}
                  />
                  {user.subscription_status === 'teste' && (
                    <Typography variant="body2" color="text.secondary">
                      Restam {user.days_until_trial_end} dias de teste
                    </Typography>
                  )}
                  {user.subscription_status === 'ativo' && (
                    <Typography variant="body2" color="text.secondary">
                      Renovação em {user.days_until_subscription_end} dias
                    </Typography>
                  )}
                </Box>
              </Box>
              
              {user.subscription_status === 'teste' && (
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => router.push('/subscription')}
                >
                  Fazer Upgrade
                </Button>
              )}
            </Box>
          </Paper>

          {/* Aviso de expiração próxima */}
          {user.subscription_status === 'teste' && user.days_until_trial_end <= 2 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <Typography variant="body1">
                <strong>⏰ Atenção:</strong> Seu período de teste termina em {user.days_until_trial_end} dia(s). 
                Faça upgrade agora para manter acesso ininterrupto à plataforma.
              </Typography>
            </Alert>
          )}
        </Box>

        {/* Estatísticas */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Assignment color="primary" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {stats.oportunidades}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Oportunidades
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TrendingUp color="secondary" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {stats.propostas}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Propostas
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Description color="success" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {stats.contratos}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Contratos
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Payment color="info" sx={{ fontSize: 40, mr: 2 }} />
                  <Box>
                    <Typography variant="h4" component="div">
                      {stats.faturas}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Faturas
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Ações rápidas */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Ações Rápidas
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => router.push('/oportunidades/nova')}
                  >
                    Nova Oportunidade
                  </Button>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => router.push('/precificacao')}
                  >
                    Precificar Item
                  </Button>
                  <Button
                    variant="outlined"
                    fullWidth
                    onClick={() => router.push('/documentos/gerar')}
                  >
                    Gerar Documento
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Notificações
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Alert severity="info">
                    <Typography variant="body2">
                      Nova oportunidade disponível em sua região
                    </Typography>
                  </Alert>
                  <Alert severity="warning">
                    <Typography variant="body2">
                      Prazo para envio da proposta vence em 2 dias
                    </Typography>
                  </Alert>
                  <Alert severity="success">
                    <Typography variant="body2">
                      Documento gerado com sucesso
                    </Typography>
                  </Alert>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Oportunidades recentes */}
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Oportunidades Recentes
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {recentOportunidades.map((oportunidade) => (
                <Box
                  key={oportunidade.id}
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    p: 2,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                  }}
                >
                  <Box>
                    <Typography variant="subtitle1" gutterBottom>
                      {oportunidade.titulo}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {oportunidade.orgao} • {oportunidade.valor}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right' }}>
                    <Chip
                      label={oportunidade.status}
                      color={
                        oportunidade.status === 'Em análise'
                          ? 'warning'
                          : oportunidade.status === 'Precificando'
                          ? 'info'
                          : 'success'
                      }
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      Prazo: {oportunidade.prazo}
                    </Typography>
                  </Box>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  )
}
