import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Button,
  Descriptions,
  Drawer,
  Input,
  Modal,
  Select,
  Table,
  Tag,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import type { Task, TaskStatus } from '../types'
import { TASK_STATUS_LABELS } from '../types'

const STATUS_TAG: Record<TaskStatus, string> = {
  unscheduled: 'default',
  scheduled: 'blue',
  testing: 'processing',
  completed: 'green',
}

export default function TasksPage() {
  const me = useMe()
  const canExecute = me?.role === 'engineer' || me?.role === 'admin'
  const isAdmin = me?.role === 'admin'
  const { message } = AntApp.useApp()

  const [rows, setRows] = useState<Task[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | undefined>(undefined)
  const [category, setCategory] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Task | null>(null)
  const [busy, setBusy] = useState(false)
  const [retestModal, setRetestModal] = useState(false)
  const [retestReason, setRetestReason] = useState('')
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(
    async (query: string, st: string | undefined, cat: string | undefined) => {
      setLoading(true)
      try {
        const params = new URLSearchParams()
        if (query.trim()) params.set('q', query.trim())
        if (st) params.set('status', st)
        if (cat) params.set('category', cat)
        const url = `/api/tasks${params.size ? `?${params}` : ''}`
        setRows(await apiFetch<Task[]>(url))
      } catch (e) {
        message.error(e instanceof Error ? e.message : '加载失败')
      } finally {
        setLoading(false)
      }
    },
    [message],
  )

  useEffect(() => {
    load('', undefined, undefined)
  }, [load])

  const onSearch = (v: string) => {
    setQ(v)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => load(v, status, category), 300)
  }

  const act = async (task: Task, action: 'start' | 'complete' | 'retest', body?: Record<string, unknown>) => {
    setBusy(true)
    try {
      const r = await apiFetch<Task>(`/api/tasks/${task.id}/${action}`, {
        method: 'POST',
        body: JSON.stringify(body ?? {}),
      })
      message.success(action === 'start' ? '测试已开始' : action === 'complete' ? '任务已完成' : '已打回重测')
      setDetail(r)
      setRetestModal(false)
      load(q, status, category)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '操作失败')
    } finally {
      setBusy(false)
    }
  }

  const columns: ColumnsType<Task> = [
    { title: '任务号', dataIndex: 'code', width: 150, render: (v: string) => <span className="cust-code">{v}</span> },
    {
      title: '委托单',
      dataIndex: 'entrustment_code',
      width: 150,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    {
      title: '样品',
      width: 170,
      render: (_, r) => (
        <span>
          <span className="cust-code">{r.sample_code}</span>{' '}
          <span style={{ fontSize: 12, color: 'var(--ink3)' }}>{r.sample_name}</span>
        </span>
      ),
    },
    { title: '项目', dataIndex: 'item_name' },
    {
      title: '类别',
      dataIndex: 'category',
      width: 80,
      render: (v: string) => (
        <Tag color={v === 'EMI' ? 'blue' : 'purple'}>{v}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      render: (v: TaskStatus) => <Tag color={STATUS_TAG[v]}>{TASK_STATUS_LABELS[v]}</Tag>,
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
        <h3>测试任务</h3>
        <span className="count">{rows.length} 条</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input placeholder="搜索任务号 / 样品 / 项目…" value={q} onChange={(e) => onSearch(e.target.value)} />
        </div>
        <Select
          allowClear
          placeholder="全部状态"
          style={{ width: 110 }}
          value={status}
          onChange={(v) => {
            setStatus(v)
            load(q, v, category)
          }}
          options={(Object.keys(TASK_STATUS_LABELS) as TaskStatus[]).map((s) => ({
            value: s,
            label: TASK_STATUS_LABELS[s],
          }))}
        />
        <Select
          allowClear
          placeholder="全部类别"
          style={{ width: 100 }}
          value={category}
          onChange={(v) => {
            setCategory(v)
            load(q, status, v)
          }}
          options={[
            { value: 'EMI', label: 'EMI' },
            { value: 'EMS', label: 'EMS' },
          ]}
        />
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
                <b>还没有测试任务</b>
                <p>任务由「确认委托」按 标准项目 × 样品 自动生成</p>
              </div>
            ),
          }}
        />
      </div>

      {/* 详情 Drawer */}
      <Drawer
        open={detail !== null}
        onClose={() => setDetail(null)}
        width={520}
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
              <Descriptions.Item label="委托单">
                <span className="cust-code">{detail.entrustment_code}</span>
              </Descriptions.Item>
              <Descriptions.Item label="样品">
                <span className="cust-code">{detail.sample_code}</span>
              </Descriptions.Item>
              <Descriptions.Item label="项目">{detail.item_name}</Descriptions.Item>
              <Descriptions.Item label="类别">
                <Tag color={detail.category === 'EMI' ? 'blue' : 'purple'}>{detail.category}</Tag>
              </Descriptions.Item>
              <Descriptions.Item label="开始时间">
                {detail.started_at ? detail.started_at.slice(0, 16).replace('T', ' ') : '—'}
              </Descriptions.Item>
              <Descriptions.Item label="完成时间">
                {detail.completed_at ? detail.completed_at.slice(0, 16).replace('T', ' ') : '—'}
              </Descriptions.Item>
              {detail.retest_reason && (
                <Descriptions.Item label="打回原因" span={2}>
                  {detail.retest_reason}
                </Descriptions.Item>
              )}
            </Descriptions>

            {canExecute && (detail.status === 'unscheduled' || detail.status === 'scheduled') && (
              <Button type="primary" loading={busy} onClick={() => act(detail, 'start')}>
                开始测试
              </Button>
            )}
            {canExecute && detail.status === 'testing' && (
              <Button type="primary" loading={busy} style={{ marginLeft: 10 }} onClick={() => act(detail, 'complete')}>
                完成任务
              </Button>
            )}
            {isAdmin && detail.status === 'completed' && (
              <Button
                danger
                loading={busy}
                style={{ marginLeft: 10 }}
                onClick={() => {
                  setRetestReason('')
                  setRetestModal(true)
                }}
              >
                打回重测
              </Button>
            )}
          </>
        )}
      </Drawer>

      {/* 打回 Modal */}
      <Modal
        open={retestModal}
        title="打回重测"
        width={440}
        onCancel={() => setRetestModal(false)}
        onOk={() => detail && act(detail, 'retest', { reason: retestReason || null })}
        okText="确认打回"
        okButtonProps={{ danger: true, loading: busy }}
        cancelText="再想想"
      >
        <p style={{ fontSize: 13, color: 'var(--ink2)', marginTop: 0 }}>
          打回后任务回到「测试中」，请说明原因（记录在案）：
        </p>
        <Input.TextArea
          rows={3}
          value={retestReason}
          onChange={(e) => setRetestReason(e.target.value)}
          placeholder="如：数据存疑 / 测试条件不符"
        />
      </Modal>
    </>
  )
}
