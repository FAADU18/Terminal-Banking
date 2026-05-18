import { Link } from 'react-router-dom'

function NotFoundPage() {
  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <div className="glass-card max-w-md p-8 text-center">
        <h1 className="font-display text-5xl font-bold text-slate-800 dark:text-slate-100">404</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-300">Page not found.</p>
        <Link className="btn-primary mt-6 inline-block" to="/dashboard">
          Go to Dashboard
        </Link>
      </div>
    </div>
  )
}

export default NotFoundPage
