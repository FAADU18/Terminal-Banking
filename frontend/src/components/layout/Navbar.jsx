import { Bell, LogOut, Menu, Moon, Sun } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function Navbar({ onMenuClick }) {
  const navigate = useNavigate()
  const { user, darkMode, setDarkMode, logout } = useAuth()

  const onLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <header className="glass-card mb-6 flex items-center justify-between px-4 py-3">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="btn-muted p-2 md:hidden"
          aria-label="Open navigation"
        >
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Welcome back</p>
          <h2 className="font-display text-lg font-semibold text-slate-800 dark:text-slate-100">
            {user?.name || user?.email || 'Customer'}
          </h2>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button type="button" className="btn-muted p-2" aria-label="Notifications">
          <Bell className="h-5 w-5" />
        </button>
        <button
          type="button"
          onClick={() => setDarkMode(!darkMode)}
          className="btn-muted p-2"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
        <button type="button" onClick={onLogout} className="btn-primary inline-flex items-center gap-2">
          <LogOut className="h-4 w-4" />
          Logout
        </button>
      </div>
    </header>
  )
}

export default Navbar
