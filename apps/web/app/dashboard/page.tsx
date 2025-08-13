'use client'

import React, { useState, useEffect } from 'react'
import { Box, Container, Typography, Grid, Card, CardContent, Paper, Chip, LinearProgress } from '@mui/material'
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
                    sx={{ fontWeight: 'bold' }}
                  />
                  {user.subscription_status !== 'ativo' && (
                    <Typography variant="body2" color="text.secondary">
                      {user.days_until_trial_end} dias restantes no período de teste
                    </Typography>
                  )}
                </Box>
              </Box>
            </Box>
          </Paper>
        </Box>

        {/* Estatísticas */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" component="div" color="primary">
                  {stats.oportunidades}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Oportunidades
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" component="div" color="primary">
                  {stats.propostas}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Propostas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" component="div" color="primary">
                  {stats.contratos}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Contratos
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" component="div" color="primary">
                  {stats.faturas}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Faturas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Oportunidades Recentes */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            Oportunidades Recentes
          </Typography>
          
          <Grid container spacing={2}>
            {recentOportunidades.map((oportunidade) => (
              <Grid item xs={12} md={6} lg={4} key={oportunidade.id}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {oportunidade.titulo}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Órgão:</strong> {oportunidade.orgao}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Valor:</strong> {oportunidade.valor}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      <strong>Prazo:</strong> {oportunidade.prazo}
                    </Typography>
                    <Chip
                      label={oportunidade.status}
                      color="primary"
                      size="small"
                      sx={{ mt: 1 }}
                    />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>
    </Container>
  )
}
