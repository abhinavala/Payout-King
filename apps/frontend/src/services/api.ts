import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Auth endpoints
export async function login(email: string, password: string) {
  const formData = new FormData()
  formData.append('username', email)
  formData.append('password', password)
  
  const response = await api.post('/auth/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function register(email: string, password: string) {
  const response = await api.post('/auth/register', { email, password })
  return response.data
}

export async function getCurrentUser(token: string) {
  const response = await axios.get(`${API_BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data
}

// Account endpoints
export async function getAccounts(token: string) {
  const response = await axios.get(`${API_BASE_URL}/accounts/`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data.accounts
}

export async function createAccount(token: string, accountData: any) {
  const response = await axios.post(`${API_BASE_URL}/accounts/`, accountData, {
    headers: { Authorization: `Bearer ${token}` },
  })
  return response.data
}

export async function deleteAccount(token: string, accountId: string) {
  await axios.delete(`${API_BASE_URL}/accounts/${accountId}`, {
    headers: { Authorization: `Bearer ${token}` },
  })
}

