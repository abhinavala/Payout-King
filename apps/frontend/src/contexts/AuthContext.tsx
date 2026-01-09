import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { login as apiLogin, getCurrentUser } from '../services/api'

interface User {
  id: string
  email: string
  createdAt: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('token')
  )
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (token) {
      getCurrentUser(token)
        .then((userData) => {
          setUser(userData)
        })
        .catch((err) => {
          console.error('Failed to get current user:', err)
          localStorage.removeItem('token')
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [token])

  const login = async (email: string, password: string) => {
    const { access_token } = await apiLogin(email, password)
    setToken(access_token)
    localStorage.setItem('token', access_token)
    const userData = await getCurrentUser(access_token)
    setUser(userData)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

