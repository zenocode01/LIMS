export interface UserOut {
  id: number
  username: string
  name: string
  role: 'business' | 'engineer' | 'admin'
  is_active: boolean
}
