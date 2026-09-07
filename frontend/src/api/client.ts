const TOKEN_KEY = 'lims_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t: string | null) =>
  t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY)

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      ...(init.headers || {}),
    },
  })
  if (res.status === 401) {
    setToken(null)
    window.location.href = '/login'
  }
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`)
  return res.status === 204 ? (undefined as T) : (await res.json() as T)
}
