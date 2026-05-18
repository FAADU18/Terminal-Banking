import api from './client'

export const loginApi = async (payload) => {
  const { data } = await api.post('/auth/login', payload)
  return data
}

export const registerApi = async (payload) => {
  const { data } = await api.post('/auth/register', payload)
  return data
}
