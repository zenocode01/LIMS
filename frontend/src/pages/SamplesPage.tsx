import { useCallback, useEffect, useRef, useState } from 'react'
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
  Timeline,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { PlusOutlined } from '@ant-design/icons'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import { dotColor } from '../theme'
import type { Entrustment, Sample, SampleStatus } from '../types'
import { SAMPLE_STATUS_LABELS } from '../types'

const STATUS_TAG: Record<SampleStatus, string> = {
  registered: 'default',
  in_test: 'processing',
  returned: 'gold',
  disposed: 'red',
}

const NEXT: Partial<Record<SampleStatus, { to: SampleStatus; label: string }>> = {
  registered: { to: 'in_test', label: '开始测试' },
  in_test: { to: 'returned', label: '样品已返' },
  returned: { to: 'disposed', label: '报废' },
}

export default function SamplesPage() {
  const me = useMe()
  const canWrite = me?.role === 'business' || me?.role === 'admin'
  const { message } = AntApp.useApp()

  const [rows, setRows] = useState<Sample[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Sample | null>(null)
  const [modal, setModal] = useState<'create' | null>(null)
  const [busy, setBusy] = useState(false)
  const [entrusts, setEntrusts] = useState<Entrustment[]>([])
  const [form] = Form.useForm()
  const [termModal, setTermModal] = useState<{ to: SampleStatus } | null>(null)
  const [termNote, setTermNote] = useState('')
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(
    async (query: string, st: string | undefined) => {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (query.trim()) params.set('q', query.trim())
        if (st) params.set('status', st)
        const url = `/api/samples${params.size ? `?${params}` : ''}`
        setRows(await apiFetch<Sample[]>(url))
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
    apiFetch<Entrustment[]>('/api/entrustments')
      .then(setEntrusts)
      .catch(() => undefined)
  }, [canWrite])

  const onSearch = (v: string) => {
    setQ(v)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => load(v, status), 300)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    setBusy(true)
    try {
      await apiFetch<Sample>('/api/samples', {
        method: 'POST',
        body: JSON.stringify({
          entrustment_id: values.entrustment_id,
          name_model: values.name_model,
          appearance: values.appearance || null,
          external_no: values.external_no || null,
        }),
      })
      message.success('样品已登记')
      setModal(null)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const doTransition = async (sample: Sample, to: SampleStatus, note: string | null) => {
    setBusy(true)
    try {
      const r = await apiFetch<Sample>(`/api/samples/${sample.id}/transition`, {
        method: 'POST',
        body: JSON.stringify({ to, note }),
      })
      message.success(`样品已「${SAMPLE_STATUS_LABELS[to]}」`)
      setDetail(r)
      setTermModal(null)
      load(q, status)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  const columns: ColumnsType<Sample> = [
    {
      title: '样品编号',
      dataIndex: 'code',
      width: 190,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    {
      title: '委托单',
      dataIndex: 'entrustment_code',
      width: 150,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    {
      title: '名称型号',
      dataIndex: 'name_model',
      render: (v: string) => (
        <span className="cust-name">
          <i className="dot" style={{ background: dotColor(v) }} />
          {v}
        </span>
      ),
    },
    {
      title: '外观',
      dataIndex: 'appearance',
      ellipsis: true,
      render: (v: string | null) => v ?? <span style={{ color: 'var(--ink3)' }}>—</span>,
    },
    {
      title: '外部单号',
      dataIndex: 'external_no',
      width: 120,
      render: (v: string | null) =>
        v ? <span className="cust-code">{v}</span> : <span style={{ color: 'var(--ink3)' }}>—</span>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (v: SampleStatus) => <Tag color={STATUS_TAG[v]}>{SAMPLE_STATUS_LABELS[v]}</Tag>,
    },
    {
      title: '登记日期',
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

  const next = detail ? NEXT[detail.status] : undefined

  return (
    <>
      <div className="page-head">
        <h3>样品</h3>
        <span className="count">{rows.length} 条</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input placeholder="搜索编号 / 名称 / 委托单号…" value={q} onChange={(e) => onSearch(e.target.value)} />
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
          options={(Object.keys(SAMPLE_STATUS_LABELS) as SampleStatus[]).map((s) => ({
            value: s,
            label: SAMPLE_STATUS_LABELS[s],
          }))}
        />
        {canWrite && (
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => setModal('create')}>
            登记样品
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
                <b>还没有样品</b>
                <p>样品挂在委托单下登记，状态每次流转都会留痕</p>
                {canWrite && (
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => setModal('create')}>
                    登记第一份样品
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
        onClose={() => setDetail(null)}
        width={560}
        title={
          detail && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="cust-code" style={{ fontSize: 15 }}>{detail.code}</span>
              <Tag color={STATUS_TAG[detail.status]}>{detail.status_label}</Tag>
            </span>
          )
        }
      >
        {detail && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 18 }}>
              <Descriptions.Item label="委托单" span={2}>
                <span className="cust-code">{detail.entrustment_code}</span>
              </Descriptions.Item>
              <Descriptions.Item label="名称型号">{detail.name_model}</Descriptions.Item>
              <Descriptions.Item label="外部单号">{detail.external_no ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="外观">{detail.appearance ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="登记人">{detail.created_by ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="登记日期" span={2}>{detail.created_at.slice(0, 10)}</Descriptions.Item>
            </Descriptions>

            {canWrite && next && (
              <div style={{ marginBottom: 18 }}>
                <Button
                  type={next.to === 'disposed' ? 'default' : 'primary'}
                  danger={next.to === 'disposed'}
                  loading={busy}
                  onClick={() => {
                    setTermNote('')
                    setTermModal({ to: next.to })
                  }}
                >
                  {next.label}
                </Button>
              </div>
            )}

            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '4px 0 10px' }}>
              流转留痕
            </div>
            <Timeline
              items={detail.events.map((ev) => ({
                color: ev.to_status === 'disposed' ? 'red' : ev.to_status === 'in_test' ? 'blue' : 'gray',
                children: (
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600 }}>
                      {ev.to_status_label}
                      {ev.note && <span style={{ fontWeight: 400, color: 'var(--ink2)' }}> · {ev.note}</span>}
                    </div>
                    <div style={{ fontSize: 11.5, color: 'var(--ink3)' }}>
                      {ev.operator ?? '—'} · {ev.created_at.replace('T', ' ').slice(0, 16)}
                    </div>
                  </div>
                ),
              }))}
            />
          </>
        )}
      </Drawer>

      {/* 登记 Modal */}
      <Modal
        open={modal !== null}
        title="登记样品"
        width={560}
        onCancel={() => setModal(null)}
        onOk={onSubmit}
        okText="登记"
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="entrustment_id" label="所属委托单" rules={[{ required: true, message: '请选择委托单' }]}>
            <Select
              showSearch
              optionFilterProp="label"
              placeholder="选择委托单"
              options={entrusts.map((e) => ({ value: e.id, label: `${e.code}（${e.customer_name}）` }))}
            />
          </Form.Item>
          <Form.Item name="name_model" label="名称 / 型号" rules={[{ required: true, message: '请输入名称型号' }]}>
            <Input placeholder="如：路由器 RT-9（Wi-Fi 6，白色）" />
          </Form.Item>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Form.Item name="appearance" label="外观状况">
              <Input placeholder="如：外壳完好，标签齐全" />
            </Form.Item>
            <Form.Item name="external_no" label="客户外部编号（选填）">
              <Input placeholder="如：SN-88231" />
            </Form.Item>
          </div>
        </Form>
      </Modal>

      {/* 流转 Modal */}
      <Modal
        open={termModal !== null}
        title={termModal && `样品流转 → ${SAMPLE_STATUS_LABELS[termModal.to]}`}
        width={440}
        onCancel={() => setTermModal(null)}
        onOk={() => detail && termModal && doTransition(detail, termModal.to, termNote || null)}
        okText="确认"
        okButtonProps={{ danger: termModal?.to === 'disposed' }}
        cancelText="再想想"
      >
        <p style={{ fontSize: 13, color: 'var(--ink2)', marginTop: 0 }}>
          本次流转将写入留痕记录，可备注说明（如寄送方式、报废原因）：
        </p>
        <Input.TextArea
          rows={3}
          value={termNote}
          onChange={(e) => setTermNote(e.target.value)}
          placeholder="备注（选填）"
        />
      </Modal>
    </>
  )
}
