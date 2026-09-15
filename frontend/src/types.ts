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

export type EntrustStatus =
  | 'draft'
  | 'confirmed'
  | 'testing'
  | 'report_issued'
  | 'completed'
  | 'terminated'

export const ENTRUST_STATUS_LABELS: Record<EntrustStatus, string> = {
  draft: '草稿',
  confirmed: '已确认',
  testing: '测试中',
  report_issued: '已出报告',
  completed: '已完成',
  terminated: '已终止',
}

export interface Entrustment {
  id: number
  code: string
  customer_id: number
  customer_name: string
  source_quote_id: number | null
  source_quote_code: string | null
  requirement: string | null
  external_no: string | null
  status: EntrustStatus
  status_label: string
  created_by: string | null
  created_at: string
  confirmed_at: string | null
  terminated_at: string | null
  terminated_by: string | null
  terminated_reason: string | null
}

export type SampleStatus = 'registered' | 'in_test' | 'returned' | 'disposed'

export const SAMPLE_STATUS_LABELS: Record<SampleStatus, string> = {
  registered: '已登记',
  in_test: '在测',
  returned: '已返',
  disposed: '已报废',
}

export interface SampleEvent {
  from_status: string | null
  to_status: string
  to_status_label: string
  operator: string | null
  note: string | null
  created_at: string
}

export interface Sample {
  id: number
  code: string
  biz_line: string
  entrustment_id: number
  entrustment_code: string
  name_model: string
  appearance: string | null
  external_no: string | null
  status: SampleStatus
  status_label: string
  created_by: string | null
  created_at: string
  events: SampleEvent[]
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
