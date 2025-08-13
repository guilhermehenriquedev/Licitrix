import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import CssBaseline from '@mui/material/CssBaseline'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '../providers/AuthProvider'
import { ThemeRegistry } from '../components/ThemeRegistry'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Licitrix - SaaS de Licitações',
  description: 'Plataforma completa para gestão de licitações públicas',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <ThemeRegistry>
          <CssBaseline />
          <AuthProvider>
            {children}
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
          </AuthProvider>
        </ThemeRegistry>
      </body>
    </html>
  )
}
