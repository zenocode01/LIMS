import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Select,
  Table,
  Tag,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { DeleteOutlined, PlusOutlined } from '@ant-design/icons'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import { dotColor } from '../theme'
import type { Customer, Quote, QuoteStatus } from '../types'
import { QUOTE_STATUS_LABELS } from '../types'

const STATUS_TAG: Record<QuoteStatus, string> = {
  draft: 'default',
  issued: 'blue',
  finalized: 'gold',
  converted: 'green',
  cancelled: 'red',
}

export function money(n: number): string {
  return `¥ ${n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

interface ItemRow {
  key: number
  item_name: string
  qty: number
  unit_price: number
}

let rowKey = 0

export default function QuotationsPage() {
  const me = useMe()
  const canWrite = me?.role === 'business'
  const { message } = AntApp.useApp()
  const location = useLocation()

  const [rows, setRows] = useState<Quote[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Quote | null>(null)
  const [modal, setModal] = useState<'create' | Quote | null>(null)
  const [busy, setBusy] = useState(false)
  const [customers, setCustomers] = useState<Customer[]>([])
  const [form] = Form.useForm()
  const [items, setItems] = useState<ItemRow[]>([{ key: rowKey++, item_name: '', qty: 1, unit_price: 0 }])
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(
    async (query: string, st: string | undefined) => {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (query.trim()) params.set('q', query.trim())
        if (st) params.set('status', st)
        const url = `/api/quotations${params.size ? `?${params}` : ''}`
        setRows(await apiFetch<Quote[]>(url))
      } catch (e) {
        message.error(e instanceof Error ? e.message : '加载失败')
      } finally {
        setLoading(false)
      }
    },
    [message],
  )

  useEffect(() => {
    load('', undefined)
  }, [load])

  useEffect(() => {
    if (!canWrite) return
    apiFetch<Customer[]>('/api/customers')
      .then((cs) => setCustomers([...cs].sort((a, b) => a.name.localeCompare(b.name))))
      .catch(() => undefined)
  }, [canWrite])

  // 从工作台「新建报价」跳来 → 直接弹建单框
  useEffect(() => {
    if ((location.state as { create?: boolean } | null)?.create && me?.role === 'business') {
      openCreate()
      window.history.replaceState({}, '')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state])

  const onSearch = (v: string) => {
    setQ(v)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => load(v, status), 300)
  }

  const total = items.reduce((s, i) => s + (i.qty || 0) * (i.unit_price || 0), 0)

  const openCreate = () => {
    form.resetFields()
    setItems([{ key: rowKey++, item_name: '', qty: 1, unit_price: 0 }])
    setModal('create')
  }

  const openEdit = (quote: Quote) => {
    form.setFieldsValue({ customer_id: quote.customer_id, remark: quote.remark })
    setItems(quote.items.map((i) => ({ key: rowKey++, ...i })))
    setModal(quote)
  }

  const setItem = (key: number, patch: Partial<ItemRow>) =>
    setItems((prev) => prev.map((i) => (i.key === key ? { ...i, ...patch } : i)))

  const onSubmit = async () => {
    const values = await form.validateFields()
    const clean = items.filter((i) => i.item_name.trim())
    if (clean.length === 0) {
      message.warning('请至少填写一条报价明细')
      return
    }
    setBusy(true)
    try {
      const payload: Record<string, unknown> = {
        items: clean.map(({ key: _k, ...rest }) => rest),
        remark: values.remark,
      }
      if (modal === 'create') payload.customer_id = values.customer_id
      if (modal === 'create') {
        await apiFetch<Quote>('/api/quotations', { method: 'POST', body: JSON.stringify(payload) })
        message.success('报价单已创建')
      } else if (modal) {
        await apiFetch<Quote>(`/api/quotations/${modal.id}`, { method: 'PATCH', body: JSON.stringify(payload) })
        message.success('已保存修改')
      }
      setModal(null)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const act = async (quote: Quote, action: 'issue' | 'finalize' | 'cancel', label: string) => {
    setBusy(true)
    try {
      const r = await apiFetch<Quote>(`/api/quotations/${quote.id}/${action}`, { method: 'POST' })
      message.success(label)
      setDetail(r)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  const columns: ColumnsType<Quote> = [
    {
      title: '编号',
      dataIndex: 'code',
      width: 150,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      render: (_, r) => (
        <span className="cust-name">
          <i className="dot" style={{ background: dotColor(r.customer_name) }} />
          {r.customer_name}
          <span className="cust-code">{r.customer_code}</span>
        </span>
      ),
    },
    { title: '明细', width: 90, render: (_, r) => `${r.items.length} 项` },
    {
      title: '合计',
      dataIndex: 'total',
      width: 130,
      align: 'right',
      render: (v: number) => <span className="cust-code">{money(v)}</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (v: QuoteStatus) => <Tag color={STATUS_TAG[v]}>{QUOTE_STATUS_LABELS[v]}</Tag>,
    },
    {
      title: '创建日期',
      dataIndex: 'created_at',
      width: 110,
      render: (v: string) => <span className="cust-date">{v.slice(0, 10)}</span>,
    },
    {
      title: '',
      width: 130,
      render: (_, r) => (
        <span>
          <Button type="link" size="small" onClick={() => setDetail(r)}>
            详情
          </Button>
          {canWrite && r.status === 'draft' && (
            <Button type="link" size="small" onClick={() => openEdit(r)}>
              编辑
            </Button>
          )}
        </span>
      ),
    },
  ]

  return (
    <>
      <div className="page-head">
        <h3>报价单</h3>
        <span className="count">{rows.length} 条</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input placeholder="搜索编号 / 客户…" value={q} onChange={(e) => onSearch(e.target.value)} />
        </div>
        <Select
          allowClear
          placeholder="全部状态"
          style={{ width: 120 }}
          value={status}
          onChange={(v) => {
            setStatus(v)
            load(q, v)
          }}
          options={(Object.keys(QUOTE_STATUS_LABELS) as QuoteStatus[]).map((s) => ({
            value: s,
            label: QUOTE_STATUS_LABELS[s],
          }))}
        />
        {canWrite && (
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={openCreate}>
            新建报价
          </Button>
        )}
      </div>

      <div className="customers-panel stagger">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={rows}
          loading={loading}
          pagination={false}
          size="middle"
          onRow={(r) => ({ onClick: () => setDetail(r), style: { cursor: 'pointer' } })}
          locale={{
            emptyText: (
              <div className="empty-invite">
                <b>还没有报价单</b>
                <p>选客户、列项目、填单价 —— 报价单是委托的起点</p>
                {canWrite && (
                  <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
                    新建第一份报价
                  </Button>
                )}
              </div>
            ),
          }}
        />
      </div>

      {/* 详情 Drawer */}
      <Drawer open={detail !== null} onClose={() => setDetail(null)} width={600} title={detail && (
        <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span className="cust-code" style={{ fontSize: 15 }}>{detail.code}</span>
          <Tag color={STATUS_TAG[detail.status as QuoteStatus]}>{QUOTE_STATUS_LABELS[detail.status as QuoteStatus]}</Tag>
        </span>
      )}>
        {detail && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 18 }}>
              <Descriptions.Item label="客户">
                {detail.customer_name} <span className="cust-code">{detail.customer_code}</span>
              </Descriptions.Item>
              <Descriptions.Item label="合计">
                <b className="cust-code">{money(detail.total)}</b>
              </Descriptions.Item>
              <Descriptions.Item label="创建日期">{detail.created_at.slice(0, 10)}</Descriptions.Item>
              <Descriptions.Item label={detail.issued_at ? '发出时间' : detail.finalized_at ? '落单时间' : '发出/落单'}>
                {detail.issued_at?.slice(0, 10) ?? detail.finalized_at?.slice(0, 10) ?? '—'}
              </Descriptions.Item>
              {detail.remark && (
                <Descriptions.Item label="备注" span={2}>{detail.remark}</Descriptions.Item>
              )}
            </Descriptions>
            <Table
              rowKey="item_name"
              size="small"
              pagination={false}
              dataSource={detail.items}
              columns={[
                { title: '项目', dataIndex: 'item_name' },
                { title: '数量', dataIndex: 'qty', width: 70, align: 'right' },
                {
                  title: '单价',
                  dataIndex: 'unit_price',
                  width: 110,
                  align: 'right',
                  render: (v: number) => <span className="cust-code">{money(v)}</span>,
                },
                {
                  title: '金额',
                  dataIndex: 'amount',
                  width: 110,
                  align: 'right',
                  render: (v: number) => <span className="cust-code">{money(v)}</span>,
                },
              ]}
            />
            {canWrite && (
              <div style={{ display: 'flex', gap: 10, marginTop: 20 }}>
                {detail.status === 'draft' && (
                  <>
                    <Button type="primary" loading={busy} onClick={() => act(detail, 'issue', '报价已发出')}>
                      发出
                    </Button>
                    <Popconfirm title="取消这份报价？" onConfirm={() => act(detail, 'cancel', '报价已取消')} okText="取消报价" cancelText="再想想">
                      <Button danger loading={busy}>取消报价</Button>
                    </Popconfirm>
                  </>
                )}
                {detail.status === 'issued' && (
                  <>
                    <Button type="primary" loading={busy} onClick={() => act(detail, 'finalize', '已落单，可转委托')}>
                      客户已接受（落单）
                    </Button>
                    <Popconfirm title="取消这份报价？" onConfirm={() => act(detail, 'cancel', '报价已取消')} okText="取消报价" cancelText="再想想">
                      <Button danger loading={busy}>取消报价</Button>
                    </Popconfirm>
                  </>
                )}
                {detail.status === 'finalized' && (
                  <Button type="primary" disabled title="委托管理模块上线后开放（T-015）">
                    一键转委托单
                  </Button>
                )}
              </div>
            )}
          </>
        )}
      </Drawer>

      {/* 新建/编辑 Modal */}
      <Modal
        open={modal !== null}
        title={modal === 'create' ? '新建报价单' : `编辑 ${modal?.code ?? ''}`}
        width={760}
        onCancel={() => setModal(null)}
        onOk={onSubmit}
        okText={modal === 'create' ? '创建' : '保存'}
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 12 }}>
            <Form.Item name="customer_id" label="客户" rules={[{ required: true, message: '请选择客户' }]}>
              <Select
                showSearch
                optionFilterProp="label"
                placeholder="选择客户"
                disabled={modal !== 'create'}
                options={customers.map((c) => ({ value: c.id, label: `${c.name}（${c.code}）` }))}
              />
            </Form.Item>
            <Form.Item label=" " colon={false}>
              {modal !== 'create' && <span className="cust-code">客户不可修改</span>}
            </Form.Item>
          </div>

          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '4px 0 10px' }}>报价明细</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 80px 120px 110px 36px', gap: 8, marginBottom: 6, fontSize: 11.5, color: 'var(--ink3)', fontWeight: 600 }}>
            <span>项目</span><span>数量</span><span>单价</span><span style={{ textAlign: 'right' }}>金额</span><span />
          </div>
          {items.map((i) => (
            <div key={i.key} style={{ display: 'grid', gridTemplateColumns: '1fr 80px 120px 110px 36px', gap: 8, marginBottom: 8, alignItems: 'center' }}>
              <Input value={i.item_name} onChange={(e) => setItem(i.key, { item_name: e.target.value })} placeholder="如：辐射发射（30m，开阔场）" />
              <InputNumber min={1} value={i.qty} onChange={(v) => setItem(i.key, { qty: v ?? 1 })} style={{ width: '100%' }} />
              <InputNumber min={0} step={100} value={i.unit_price} onChange={(v) => setItem(i.key, { unit_price: v ?? 0 })} style={{ width: '100%' }} addonBefore="¥" />
              <span className="cust-code" style={{ textAlign: 'right' }}>{money((i.qty || 0) * (i.unit_price || 0))}</span>
              <Button type="text" danger icon={<DeleteOutlined />} disabled={items.length === 1} onClick={() => setItems((prev) => prev.filter((x) => x.key !== i.key))} />
            </div>
          ))}
          <Button icon={<PlusOutlined />} type="dashed" block onClick={() => setItems((prev) => [...prev, { key: rowKey++, item_name: '', qty: 1, unit_price: 0 }])}>
            添加明细
          </Button>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--line)' }}>
            <span style={{ fontSize: 13, color: 'var(--ink2)' }}>
              共 {items.length} 项 · 合计 <b className="cust-code" style={{ fontSize: 17 }}>{money(total)}</b>
            </span>
            <Form.Item name="remark" noStyle>
              <Input style={{ width: 300 }} placeholder="备注（选填）" />
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </>
  )
}
