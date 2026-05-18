import api from './client'

export const getDashboardApi = async () => {
  const { data } = await api.get('/dashboard')
  return data
}

export const depositApi = async (payload) => {
  const { data } = await api.post('/transactions/deposit', payload)
  return data
}

export const withdrawApi = async (payload) => {
  const { data } = await api.post('/transactions/withdraw', payload)
  return data
}

export const transferApi = async (payload) => {
  const { data } = await api.post('/transactions/transfer', payload)
  return data
}

export const transactionsApi = async () => {
  const { data } = await api.get('/transactions/history')
  return data
}

export const miniStatementApi = async () => {
  const { data } = await api.get('/transactions/mini-statement')
  return data
}
