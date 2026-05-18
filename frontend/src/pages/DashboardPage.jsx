import { useEffect, useState } from 'react'
import BalanceCards from '../components/dashboard/BalanceCards'
import AnalyticsChart from '../components/dashboard/AnalyticsChart'
import NotificationsPanel from '../components/dashboard/NotificationsPanel'
import { getDashboardApi } from '../api/bankApi'
import { fallbackDashboard } from '../data/mockData'

function DashboardPage() {
  const [data, setData] = useState(fallbackDashboard)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const apiData = await getDashboardApi()
        setData({
          stats: apiData.stats || fallbackDashboard.stats,
          analytics: apiData.analytics || fallbackDashboard.analytics,
          notifications: apiData.notifications || fallbackDashboard.notifications,
        })
      } catch (err) {
        setError(err?.response?.data?.message || 'Showing fallback analytics. Connect Flask API for live data.')
      }
    }

    fetchDashboard()
  }, [])

  return (
    <div className="space-y-5">
      {error ? <p className="rounded-xl bg-amber-100 p-3 text-sm text-amber-700">{error}</p> : null}
      <BalanceCards stats={data.stats} />
      <div className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <AnalyticsChart data={data.analytics} />
        <NotificationsPanel items={data.notifications} />
      </div>
    </div>
  )
}

export default DashboardPage
