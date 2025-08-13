'use client'

import React from 'react'
import { Box, Container, Typography, Button } from '@mui/material'
import { useRouter } from 'next/navigation'

export default function NotFound() {
  const router = useRouter()

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
        }}
      >
        <Typography variant="h1" component="h1" gutterBottom>
          404
        </Typography>
        <Typography variant="h4" component="h2" gutterBottom>
          Página não encontrada
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          A página que você está procurando não existe ou foi movida.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => router.push('/')}
          size="large"
        >
          Voltar ao Início
        </Button>
      </Box>
    </Container>
  )
}
