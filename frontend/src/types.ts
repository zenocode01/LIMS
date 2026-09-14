export interface UserOut {
  id: number
  username: string
  name: string
  role: 'business' | 'engineer' | 'admin'
  is_active: boolean
}

export type QuoteStatus = 'draft' | 'issued' | 'finalized' | 'converted' | 'cancelled'

export const QUOTE_STATUS_LABELS: Record<QuoteStatus, string> = {
  draft: '草稿',
  issued: '已发出',
  finalized: '已落单',
  converted: '已转委托',
  cancelled: '已取消',
}

export interface QuoteItemOut {
  item_name: string
  qty: number
  unit_price: number
  amount: number
}

export interface Quote {
  id: number
  code: string
  status: QuoteStatus
  remark: string | null
  customer_id: number
  customer_name: string
  customer_code: string
  items: QuoteItemOut[]
  total: number
  created_at: string
  updated_at: string
  issued_at: string | null
  finalized_at: string | null
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
