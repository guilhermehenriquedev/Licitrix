'use client'

import React, { useState, useEffect, createContext } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  username: string
  subscription_status: string
  is_in_trial_period: boolean
  has_active_access: boolean
  data_inicio_teste: string
  data_fim_teste: string
  plano_ativo: boolean
  data_inicio_plano: string
  data_fim_plano: string
  days_until_trial_end: number
  days_until_subscription_end: number
  created_at: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  register: (userData: any) => Promise<boolean>
  logout: () => void
  checkAuth: () => Promise<void>
  refreshToken: () => Promise<boolean>
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      const response = await fetch('/api/users/profile/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Token inválido, tentar refresh
        const refreshed = await refreshToken()
        if (!refreshed) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        }
      }
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (!refreshToken) return false

      const response = await fetch('/api/users/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      })

      if (response.ok) {
        const result = await response.json()
        localStorage.setItem('access_token', result.access)
        localStorage.setItem('refresh_token', result.refresh)
        return true
      }
    } catch (error) {
      console.error('Erro ao renovar token:', error)
    }
    return false
  }

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/users/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      })

      const result = await response.json()

      if (response.ok) {
        localStorage.setItem('access_token', result.tokens.access)
        localStorage.setItem('refresh_token', result.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(result.user))
        setUser(result.user)
        toast.success('Login realizado com sucesso!')
        return true
      } else {
        toast.error(result.error || 'Erro no login')
        return false
      }
    } catch (error) {
      toast.error('Erro de conexão')
      return false
    }
  }

  const register = async (userData: any): Promise<boolean> => {
    try {
      const response = await fetch('/api/users/auth/register/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      const result = await response.json()

      if (response.ok) {
        localStorage.setItem('access_token', result.tokens.access)
        localStorage.setItem('refresh_token', result.tokens.refresh)
        localStorage.setItem('user', JSON.stringify(result.user))
        setUser(result.user)
        toast.success('Conta criada com sucesso! Você tem 7 dias de teste gratuito.')
        return true
      } else {
        toast.error(result.error || 'Erro no registro')
        return false
      }
    } catch (error) {
      toast.error('Erro de conexão')
      return false
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    setUser(null)
    toast.success('Logout realizado com sucesso!')
    router.push('/auth/login')
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    register,
    logout,
    checkAuth,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
