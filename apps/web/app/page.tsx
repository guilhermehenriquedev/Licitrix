'use client'

import { useState } from 'react'
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material'
import {
  Business,
  Description,
  TrendingUp,
  Assignment,
  AttachMoney,
  Notifications,
  Add,
  Visibility,
} from '@mui/icons-material'

export default function Dashboard() {
  const [stats] = useState({
    oportunidades: 12,
    propostas: 5,
    contratos: 3,
    faturas: 8,
  })

  const [recentOportunidades] = useState([
    {
      id: 1,
      numero: '001/2024',
      orgao: 'Prefeitura Municipal',
      objeto: 'Fornecimento de Material de Escritório',
      valor: 'R$ 25.000,00',
      prazo: '15 dias',
      status: 'nova',
    },
    {
      id: 2,
      numero: '002/2024',
      orgao: 'Secretaria de Educação',
      objeto: 'Serviços de Limpeza',
      valor: 'R$ 45.000,00',
      prazo: '30 dias',
      status: 'analisando',
    },
  ])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'nova':
        return 'primary'
      case 'analisando':
        return 'warning'
      case 'proposta_enviada':
        return 'info'
      case 'vencedora':
        return 'success'
      default:
        return 'default'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'nova':
        return 'Nova'
      case 'analisando':
        return 'Analisando'
      case 'proposta_enviada':
        return 'Proposta Enviada'
      case 'vencedora':
        return 'Vencedora'
      default:
        return status
    }
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard Licitrix
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bem-vindo ao seu painel de controle de licitações
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Description />
                </Avatar>
                <Typography variant="h6" component="div">
                  Oportunidades
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ mb: 1 }}>
                {stats.oportunidades}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Novas oportunidades disponíveis
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <Assignment />
                </Avatar>
                <Typography variant="h6" component="div">
                  Propostas
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ mb: 1 }}>
                {stats.propostas}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Propostas em análise
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <Business />
                </Avatar>
                <Typography variant="h6" component="div">
                  Contratos
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ mb: 1 }}>
                {stats.contratos}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Contratos ativos
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <AttachMoney />
                </Avatar>
                <Typography variant="h6" component="div">
                  Faturas
                </Typography>
              </Box>
              <Typography variant="h4" component="div" sx={{ mb: 1 }}>
                {stats.faturas}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Faturas pendentes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ações Rápidas
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  size="small"
                >
                  Nova Oportunidade
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Description />}
                  size="small"
                >
                  Upload Edital
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUp />}
                  size="small"
                >
                  Precificar
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
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Notifications color="warning" />
                <Typography variant="body2">
                  3 novas oportunidades para seu perfil
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                <AttachMoney color="info" />
                <Typography variant="body2">
                  2 faturas vencem esta semana
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Recent Opportunities */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Oportunidades Recentes
              </Typography>
              <List>
                {recentOportunidades.map((oportunidade, index) => (
                  <Box key={oportunidade.id}>
                    <ListItem>
                      <ListItemIcon>
                        <Description color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="subtitle1">
                              {oportunidade.numero} - {oportunidade.orgao}
                            </Typography>
                            <Chip
                              label={getStatusLabel(oportunidade.status)}
                              color={getStatusColor(oportunidade.status)}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              {oportunidade.objeto}
                            </Typography>
                            <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                              <Typography variant="body2" color="text.primary">
                                {oportunidade.valor}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                Prazo: {oportunidade.prazo}
                              </Typography>
                            </Box>
                          </Box>
                        }
                      />
                      <Button
                        variant="outlined"
                        size="small"
                        startIcon={<Visibility />}
                      >
                        Ver Detalhes
                      </Button>
                    </ListItem>
                    {index < recentOportunidades.length - 1 && <Divider />}
                  </Box>
                ))}
              </List>
            </CardContent>
            <CardActions>
              <Button size="small" color="primary">
                Ver Todas as Oportunidades
              </Button>
            </CardActions>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Resumo Financeiro
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Valor Total em Contratos
                </Typography>
                <Typography variant="h5" color="success.main">
                  R$ 125.000,00
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Faturas a Receber
                </Typography>
                <Typography variant="h5" color="info.main">
                  R$ 45.000,00
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Próximo Vencimento
                </Typography>
                <Typography variant="h6" color="warning.main">
                  R$ 15.000,00
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Vence em 3 dias
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  )
}
