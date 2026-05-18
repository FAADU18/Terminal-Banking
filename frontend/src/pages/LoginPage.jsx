import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const from = location.state?.from?.pathname || '/dashboard'

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(form)
      navigate(from, { replace: true })
    } catch (err) {
      setError(err?.response?.data?.message || err?.message || 'Login failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-8">
      <div className="glass-card w-full max-w-md p-7">
        <h1 className="font-display text-3xl font-bold text-slate-800 dark:text-slate-100">Welcome Back</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Secure login to your banking dashboard</p>
        <p className="mt-2 rounded-lg bg-sky-50 px-3 py-2 text-xs text-sky-700 dark:bg-slate-800 dark:text-sky-300">
          If backend is offline, use demo@bank.com / password123 or register a new local account.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <input
            className="field-input"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))}
            required
          />
          <input
            className="field-input"
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))}
            required
          />

          {error ? <p className="text-sm text-rose-600">{error}</p> : null}

          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-60">
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="mt-5 text-sm text-slate-600 dark:text-slate-300">
          No account?{' '}
          <Link className="font-semibold text-brand-700" to="/register">
            Create one
          </Link>
        </p>
      </div>
    </div>
  )
}

export default LoginPage
