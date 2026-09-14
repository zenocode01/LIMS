export interface UserOut {
  id: number
  username: string
  name: string
  role: 'business' | 'engineer' | 'admin'
  is_active: boolean
}

export interface Customer {
  id: number
  code: string
  name: string
  industry: string | null
  contact_name: string | null
  contact_phone: string | null
  remark: string | null
  created_at: string
  updated_at: string
}
