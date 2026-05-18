import { Outlet } from 'react-router-dom'
import { useState } from 'react'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

function AppLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen md:grid md:grid-cols-[18rem_1fr]">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <main className="px-4 py-6 md:px-8">
        <Navbar onMenuClick={() => setIsSidebarOpen((v) => !v)} />
        <Outlet />
      </main>
    </div>
  )
}

export default AppLayout
