import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  Modal,
  Select,
  Table,
  Tag,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { PlusOutlined } from '@ant-design/icons'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import { dotColor } from '../theme'
import type { Customer, Entrustment, EntrustStatus, Sample, SampleStatus } from '../types'
import { ENTRUST_STATUS_LABELS, SAMPLE_STATUS_LABELS } from '../types'

const STATUS_TAG: Record<EntrustStatus, string> = {
  draft: 'default',
  confirmed: 'blue',
  testing: 'processing',
  report_issued: 'gold',
  completed: 'green',
  terminated: 'red',
}

const SAMPLE_TAG: Record<SampleStatus, string> = {
  registered: 'default',
  in_test: 'processing',
  returned: 'gold',
  disposed: 'red',
}

export default function EntrustmentsPage() {
  const me = useMe()
  const canWrite = me?.role === 'business' || me?.role === 'admin'
  const canTerminate = me?.role === 'admin'
  const { message } = AntApp.useApp()
  const location = useLocation()

  const [rows, setRows] = useState<Entrustment[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Entrustment | null>(null)
  const [modal, setModal] = useState<'create' | null>(null)
  const [busy, setBusy] = useState(false)
  const [customers, setCustomers] = useState<Customer[]>([])
  const [form] = Form.useForm()
  const [termModal, setTermModal] = useState(false)
  const [termReason, setTermReason] = useState('')
  const [samples, setSamples] = useState<Sample[]>([])
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const loadSamples = (entrustId: number) => {
    apiFetch<Sample[]>(`/api/samples?entrustment_id=${entrustId}`)
      .then(setSamples)
      .catch(() => setSamples([]))
  }

  const load = useCallback(
    async (query: string, st: string | undefined) => {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (query.trim()) params.set('q', query.trim())
        if (st) params.set('status', st)
        const url = `/api/entrustments${params.size ? `?${params}` : ''}`
        setRows(await apiFetch<Entrustment[]>(url))
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

  // 从工作台「新建委托」跳来 → 直接弹建单框
  useEffect(() => {
    if ((location.state as { create?: boolean } | null)?.create && canWrite) {
      setModal('create')
      window.history.replaceState({}, '')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.state])

  const onSearch = (v: string) => {
    setQ(v)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => load(v, status), 300)
  }

  const openCreate = () => {
    form.resetFields()
    setModal('create')
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    setBusy(true)
    try {
      await apiFetch<Entrustment>('/api/entrustments', {
        method: 'POST',
        body: JSON.stringify({
          customer_id: values.customer_id,
          requirement: values.requirement || null,
          external_no: values.external_no || null,
        }),
      })
      message.success('委托单已创建')
      setModal(null)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const act = async (entrust: Entrustment, action: 'confirm' | 'terminate', body?: Record<string, unknown>) => {
    setBusy(true)
    try {
      const r = await apiFetch<Entrustment>(`/api/entrustments/${entrust.id}/${action}`, {
        method: 'POST',
        body: JSON.stringify(body ?? {}),
      })
      message.success(action === 'confirm' ? '委托已确认' : '委托已终止')
      setDetail(r)
      loadSamples(r.id)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  const columns: ColumnsType<Entrustment> = [
    {
      title: '编号',
      dataIndex: 'code',
      width: 150,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    {
      title: '客户',
      dataIndex: 'customer_name',
      render: (v: string) => (
        <span className="cust-name">
          <i className="dot" style={{ background: dotColor(v) }} />
          {v}
        </span>
      ),
    },
    {
      title: '来源报价',
      dataIndex: 'source_quote_code',
      width: 150,
      render: (v: string | null) =>
        v ? <span className="cust-code">{v}</span> : <span style={{ color: 'var(--ink3)' }}>手工建单</span>,
    },
    {
      title: '外部单号',
      dataIndex: 'external_no',
      width: 130,
      render: (v: string | null) =>
        v ? <span className="cust-code">{v}</span> : <span style={{ color: 'var(--ink3)' }}>—</span>,
    },
    {
      title: '委托要求',
      dataIndex: 'requirement',
      ellipsis: true,
      render: (v: string | null) =>
        v ? <span style={{ whiteSpace: 'nowrap' }}>{v}</span> : <span style={{ color: 'var(--ink3)' }}>—</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (v: EntrustStatus) => <Tag color={STATUS_TAG[v]}>{ENTRUST_STATUS_LABELS[v]}</Tag>,
    },
    {
      title: '创建日期',
      dataIndex: 'created_at',
      width: 110,
      render: (v: string) => <span className="cust-date">{v.slice(0, 10)}</span>,
    },
    {
      title: '',
      width: 80,
      render: (_, r) => (
        <Button type="link" size="small" onClick={() => setDetail(r)}>
          详情
        </Button>
      ),
    },
  ]

  return (
    <>
      <div className="page-head">
        <h3>委托单</h3>
        <span className="count">{rows.length} 条</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input placeholder="搜索编号 / 客户 / 外部单号…" value={q} onChange={(e) => onSearch(e.target.value)} />
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
          options={(Object.keys(ENTRUST_STATUS_LABELS) as EntrustStatus[]).map((s) => ({
            value: s,
            label: ENTRUST_STATUS_LABELS[s],
          }))}
        />
        {canWrite && (
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={openCreate}>
            新建委托
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
                <b>还没有委托单</b>
                <p>已落单的报价可一键转入，也可以在这里手工建单</p>
                {canWrite && (
                  <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
                    新建第一份委托
                  </Button>
                )}
              </div>
            ),
          }}
        />
      </div>

      {/* 详情 Drawer */}
      <Drawer
        open={detail !== null}
        onClose={() => {
          setDetail(null)
          setSamples([])
        }}
        width={560}
        title={
          detail && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="cust-code" style={{ fontSize: 15 }}>{detail.code}</span>
              <Tag color={STATUS_TAG[detail.status]}>{detail.status_label}</Tag>
            </span>
          )
        }
        afterOpenChange={(open) => {
          if (open && detail) loadSamples(detail.id)
        }}
      >
        {detail && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 18 }}>
              <Descriptions.Item label="客户">{detail.customer_name}</Descriptions.Item>
              <Descriptions.Item label="创建人">{detail.created_by ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="来源报价">
                {detail.source_quote_code ? (
                  <span className="cust-code">{detail.source_quote_code}</span>
                ) : (
                  '手工建单'
                )}
              </Descriptions.Item>
              <Descriptions.Item label="外部单号">{detail.external_no ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="创建日期">{detail.created_at.slice(0, 10)}</Descriptions.Item>
              <Descriptions.Item label="确认时间">{detail.confirmed_at ? detail.confirmed_at.slice(0, 10) : '—'}</Descriptions.Item>
              {detail.status === 'terminated' && (
                <>
                  <Descriptions.Item label="终止时间">{detail.terminated_at?.slice(0, 10) ?? '—'}</Descriptions.Item>
                  <Descriptions.Item label="终止原因" span={2}>
                    {detail.terminated_reason ?? '—'}（操作人 {detail.terminated_by ?? '—'}）
                  </Descriptions.Item>
                </>
              )}
            </Descriptions>

            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '0 0 8px' }}>委托要求</div>
            <div
              style={{
                background: 'var(--panel2, #f6f8fb)',
                border: '1px solid var(--line)',
                borderRadius: 10,
                padding: '10px 12px',
                fontSize: 13,
                whiteSpace: 'pre-wrap',
                color: 'var(--ink)',
                marginBottom: 18,
                minHeight: 40,
              }}
            >
              {detail.requirement || '（未填写）'}
            </div>

            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '4px 0 8px' }}>
              样品（{samples.length}）
            </div>
            {samples.length === 0 ? (
              <div style={{ fontSize: 12.5, color: 'var(--ink3)', border: '1px dashed var(--line)', borderRadius: 10, padding: '10px 12px', marginBottom: 18 }}>
                尚未登记样品 —— 到「样品管理」里登记
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 18 }}>
                {samples.map((s) => (
                  <div
                    key={s.id}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      border: '1px solid var(--line)',
                      borderRadius: 10,
                      padding: '8px 12px',
                      fontSize: 13,
                    }}
                  >
                    <span className="cust-code">{s.code}</span>
                    <span style={{ flex: 1 }}>{s.name_model}</span>
                    <Tag color={SAMPLE_TAG[s.status]}>{SAMPLE_STATUS_LABELS[s.status]}</Tag>
                  </div>
                ))}
              </div>
            )}

            {canWrite && detail.status === 'draft' && (
              <Button type="primary" loading={busy} onClick={() => act(detail, 'confirm')}>
                确认委托
              </Button>
            )}
            {canTerminate && detail.status !== 'completed' && detail.status !== 'terminated' && (
              <Button
                danger
                loading={busy}
                style={{ marginLeft: canWrite && detail.status === 'draft' ? 10 : 0 }}
                onClick={() => {
                  setTermReason('')
                  setTermModal(true)
                }}
              >
                终止委托
              </Button>
            )}
          </>
        )}
      </Drawer>

      {/* 新建 Modal */}
      <Modal
        open={modal !== null}
        title="新建委托单"
        width={560}
        onCancel={() => setModal(null)}
        onOk={onSubmit}
        okText="创建"
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="customer_id" label="客户" rules={[{ required: true, message: '请选择客户' }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="选择客户"
              options={customers.map((c) => ({ value: c.id, label: `${c.name}（${c.code}）` }))}
            />
          </Form.Item>
          <Form.Item name="requirement" label="委托要求">
            <Input.TextArea rows={4} placeholder={'如：\n辐射发射（30m，开阔场）\n辐射抗扰度（GB/T 17626.3）'} />
          </Form.Item>
          <Form.Item name="external_no" label="客户外部单号（选填，对账用）">
            <Input placeholder="如：QT-2026-018" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 终止 Modal */}
      <Modal
        open={termModal}
        title="终止委托"
        width={440}
        onCancel={() => setTermModal(false)}
        onOk={() => {
          setTermModal(false)
          if (detail) act(detail, 'terminate', { reason: termReason || null })
        }}
        okText="确认终止"
        okButtonProps={{ danger: true, loading: busy }}
        cancelText="再想想"
      >
        <p style={{ fontSize: 13, color: 'var(--ink2)', marginTop: 0 }}>
          终止后委托单进入终态，不可再流转。请简要说明原因：
        </p>
        <Input.TextArea
          rows={3}
          value={termReason}
          onChange={(e) => setTermReason(e.target.value)}
          placeholder="如：客户撤单 / 项目取消"
        />
      </Modal>
    </>
  )
}
