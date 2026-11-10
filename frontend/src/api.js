const API = '/api'
export async function api(path, {token, ...options} = {}) {
  const headers = {...(options.headers || {})}
  if (token) headers.Authorization = `Bearer ${token}`
  if (options.body) headers['Content-Type'] = 'application/json'
  const response = await fetch(`${API}${path}`, {...options, headers})
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map(error => error.msg).filter(Boolean).join(', ')
      : data.detail
    throw new Error(detail || 'Request failed')
  }
  return data
}
