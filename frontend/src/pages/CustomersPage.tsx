import { useCallback, useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Button, Form, Input, Modal, Popconfirm, Table, App as AntApp } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import { dotColor } from '../theme'
import type { Customer } from '../types'

export default function CustomersPage() {
  const me = useMe()
  const canWrite = me?.role === 'business'
  const { message } = AntApp.useApp()

  const [rows, setRows] = useState<Customer[]>([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [modal, setModal] = useState<'create' | Customer | null>(null)
  const [busy, setBusy] = useState(false)
  const [form] = Form.useForm()
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)

  const load = useCallback(async (query: string) => {
    setLoading(true)
    try {
      const url = query.trim() ? `/api/customers?q=${encodeURIComponent(query.trim())}` : '/api/customers'
      setRows(await apiFetch<Customer[]>(url))
    } catch (e) {
      message.error(e instanceof Error ? e.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    load('')
  }, [load])

  // 从工作台“新建客户”跳来 → 直接弹建档框
  const location = useLocation()
  useEffect(() => {
    if ((location.state as { create?: boolean } | null)?.create && me?.role === 'business') {
      form.resetFields()
      setModal('create')
      window.history.replaceState({}, '')
    }
  }, [location.state, me?.role, form])

  const onSearch = (v: string) => {
    setQ(v)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => load(v), 300)
  }

  const openCreate = () => {
    form.resetFields()
    setModal('create')
  }

  const openEdit = (c: Customer) => {
    form.setFieldsValue(c)
    setModal(c)
  }

  const onSubmit = async () => {
    const values = await form.validateFields()
    setBusy(true)
    try {
      if (modal === 'create') {
        await apiFetch<Customer>('/api/customers', {
          method: 'POST',
          body: JSON.stringify(values),
        })
        message.success('客户已建档')
      } else if (modal) {
        await apiFetch<Customer>(`/api/customers/${modal.id}`, {
          method: 'PATCH',
          body: JSON.stringify(values),
        })
        message.success('已保存修改')
      }
      setModal(null)
      load(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const onDelete = async (c: Customer) => {
    try {
      await apiFetch<void>(`/api/customers/${c.id}`, { method: 'DELETE' })
      message.success(`已删除 ${c.name}`)
      load(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '删除失败')
    }
  }

  const columns: ColumnsType<Customer> = [
    {
      title: '客户',
      dataIndex: 'name',
      render: (_, c) => (
        <span className="cust-name">
          <i className="dot" style={{ background: dotColor(c.name) }} />
          {c.name}
        </span>
      ),
    },
    {
      title: '编号',
      dataIndex: 'code',
      width: 110,
      render: (v: string) => <span className="cust-code">{v}</span>,
    },
    { title: '行业', dataIndex: 'industry', width: 130, render: (v) => v ?? '—' },
    {
      title: '联系人',
      width: 190,
      render: (_, c) =>
        c.contact_name || c.contact_phone ? (
          <span className="cust-contact">
            {c.contact_name ?? ''}
            {c.contact_name && c.contact_phone ? ' · ' : ''}
            {c.contact_phone ?? ''}
          </span>
        ) : (
          '—'
        ),
    },
    { title: '备注', dataIndex: 'remark', ellipsis: true, render: (v) => v ?? '—' },
    {
      title: '建档日期',
      dataIndex: 'created_at',
      width: 110,
      render: (v: string) => <span className="cust-date">{v.slice(0, 10)}</span>,
    },
    ...(canWrite
      ? [
          {
            title: '',
            width: 110,
            render: (_: unknown, c: Customer) => (
              <span>
                <Button type="link" size="small" onClick={() => openEdit(c)}>
                  编辑
                </Button>
                <Popconfirm title={`删除客户 ${c.name}？`} onConfirm={() => onDelete(c)} okText="删除" cancelText="取消" okButtonProps={{ danger: true }}>
                  <Button type="link" size="small" danger>
                    删除
                  </Button>
                </Popconfirm>
              </span>
            ),
          },
        ]
      : []),
  ]

  return (
    <>
      <div className="page-head">
        <h3>客户档案</h3>
        <span className="count">{rows.length} 条</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input
            placeholder="搜索名称 / 编号 / 行业…"
            value={q}
            onChange={(e) => onSearch(e.target.value)}
          />
        </div>
        {canWrite && (
          <Button type="primary" size="large" onClick={openCreate}>
            新建客户
          </Button>
        )}
      </div>

      <div className="customers-panel">
        <Table
          rowKey="id"
          columns={columns}
          dataSource={rows}
          loading={loading}
          pagination={false}
          size="middle"
          locale={{
            emptyText: (
              <div className="empty-invite">
                <b>还没有客户</b>
                <p>客户是报价与委托的起点 —— 先建档，再开单</p>
                {canWrite && (
                  <Button type="primary" onClick={openCreate}>
                    新建第一个客户
                  </Button>
                )}
              </div>
            ),
          }}
        />
      </div>

      <Modal
        open={modal !== null}
        title={modal === 'create' ? '新建客户' : `编辑 ${modal?.name ?? ''}`}
        onCancel={() => setModal(null)}
        onOk={onSubmit}
        okText={modal === 'create' ? '建档' : '保存'}
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          {modal !== 'create' && (
            <div style={{ marginBottom: 14, fontSize: 13, color: 'var(--ink3)' }}>
              编号 <span className="cust-code">{modal?.code}</span>
              （静态递增，不可修改）
            </div>
          )}
          <Form.Item name="name" label="客户名称" rules={[{ required: true, message: '请输入客户名称' }]}>
            <Input placeholder="如：华为终端" />
          </Form.Item>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Form.Item name="industry" label="行业">
              <Input placeholder="如：消费电子" />
            </Form.Item>
            <Form.Item name="contact_name" label="联系人">
              <Input placeholder="如：李工" />
            </Form.Item>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Form.Item name="contact_phone" label="联系电话">
              <Input placeholder="手机号 / 座机" />
            </Form.Item>
            <Form.Item name="remark" label="备注">
              <Input placeholder="选填" />
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </>
  )
}
