import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { loginApi, registerApi } from '../api/authApi'

const AuthContext = createContext(null)
const MOCK_USERS_KEY = 'mock_users'

const seedMockUser = {
  name: 'Demo User',
  email: 'demo@bank.com',
  password: 'password123',
}

function readMockUsers() {
  const raw = localStorage.getItem(MOCK_USERS_KEY)
  if (!raw) {
    localStorage.setItem(MOCK_USERS_KEY, JSON.stringify([seedMockUser]))
    return [seedMockUser]
  }
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed) && parsed.length > 0) {
      return parsed
    }
  } catch {
    // Reset to a known-good structure on malformed local data.
  }
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify([seedMockUser]))
  return [seedMockUser]
}

function writeMockUsers(users) {
  localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users))
}

function isApiUnavailable(err) {
  return !err?.response || err?.code === 'ERR_NETWORK' || err?.response?.status >= 500
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user')
    return stored ? JSON.parse(stored) : null
  })
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true')

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode)
    localStorage.setItem('darkMode', String(darkMode))
  }, [darkMode])

  const login = async (payload) => {
    try {
      const data = await loginApi(payload)
      const nextToken = data.token || data.access_token
      const nextUser = data.user || { name: payload.email, email: payload.email }

      if (!nextToken) {
        throw new Error('Login response missing token.')
      }

      setToken(nextToken)
      setUser(nextUser)
      localStorage.setItem('token', nextToken)
      localStorage.setItem('user', JSON.stringify(nextUser))
      return data
    } catch (err) {
      if (!isApiUnavailable(err)) {
        throw err
      }

      const users = readMockUsers()
      const matched = users.find(
        (u) => u.email?.toLowerCase() === payload.email?.toLowerCase() && u.password === payload.password,
      )

      if (!matched) {
        throw new Error('Backend unavailable. Use a registered local account or demo@bank.com / password123.')
      }

      const localToken = `local-token-${Date.now()}`
      const nextUser = { name: matched.name, email: matched.email }
      setToken(localToken)
      setUser(nextUser)
      localStorage.setItem('token', localToken)
      localStorage.setItem('user', JSON.stringify(nextUser))
      return { token: localToken, user: nextUser, mode: 'local-fallback' }
    }
  }

  const register = async (payload) => {
    try {
      const data = await registerApi(payload)
      return data
    } catch (err) {
      if (!isApiUnavailable(err)) {
        throw err
      }

      const users = readMockUsers()
      const exists = users.some((u) => u.email?.toLowerCase() === payload.email?.toLowerCase())
      if (exists) {
        throw new Error('A local account with this email already exists.')
      }

      users.push({
        name: payload.name,
        email: payload.email,
        password: payload.password,
      })
      writeMockUsers(users)
      return { message: 'Registered locally (offline mode).' }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      darkMode,
      setDarkMode,
      login,
      register,
      logout,
    }),
    [user, token, darkMode],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
