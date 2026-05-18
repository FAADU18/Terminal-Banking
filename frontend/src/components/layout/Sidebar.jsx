import { CreditCard, Gauge, HandCoins, History, Landmark, Repeat, SendHorizontal } from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: Gauge },
  { to: '/deposit', label: 'Deposit', icon: HandCoins },
  { to: '/withdraw', label: 'Withdraw', icon: Landmark },
  { to: '/transfer', label: 'Transfer', icon: SendHorizontal },
  { to: '/history', label: 'History', icon: History },
  { to: '/mini-statement', label: 'Mini Statement', icon: Repeat },
]

function Sidebar({ isOpen, onClose }) {
  return (
    <aside
      className={`fixed left-0 top-0 z-40 h-full w-72 transform border-r border-white/20 bg-slate-950/70 p-5 text-slate-100 backdrop-blur-xl transition md:static md:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div className="mb-8 flex items-center gap-3">
        <div className="rounded-xl bg-banking-gradient p-2">
          <CreditCard className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="font-display text-lg font-semibold">NeoBank Pro</h1>
          <p className="text-xs text-slate-300">Smart Banking Suite</p>
        </div>
      </div>

      <nav className="space-y-2">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                isActive
                  ? 'bg-white/20 text-white shadow'
                  : 'text-slate-200 hover:bg-white/10 hover:text-white'
              }`
            }
          >
            <Icon className="h-4 w-4" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
