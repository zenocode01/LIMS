import { useEffect, useState } from 'react'
import {
  Button,
  Descriptions,
  Drawer,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Table,
  Tag,
  Tabs,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import type { Equipment, Standard } from '../types'

interface ItemRow {
  key: number
  name: string
  category: 'EMI' | 'EMS'
  method: string
  criteria: string
}

let rowKey = 0

export default function StandardsPage() {
  const me = useMe()
  const isAdmin = me?.role === 'admin'
  const { message } = AntApp.useApp()

  const [tab, setTab] = useState('standards')
  const [standards, setStandards] = useState<Standard[]>([])
  const [equipment, setEquipment] = useState<Equipment[]>([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<Standard | null>(null)
  const [stdModal, setStdModal] = useState<'create' | Standard | null>(null)
  const [items, setItems] = useState<ItemRow[]>([])
  const [eqModal, setEqModal] = useState<'create' | Equipment | null>(null)
  const [busy, setBusy] = useState(false)
  const [stdForm] = Form.useForm()
  const [eqForm] = Form.useForm()

  const loadStandards = async (query: string) => {
    setLoading(true)
    try {
      const url = `/api/standards${query.trim() ? `?q=${encodeURIComponent(query.trim())}` : ''}`
      setStandards(await apiFetch<Standard[]>(url))
    } catch (e) {
      message.error(e instanceof Error ? e.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const loadEquipment = async () => {
    try {
      setEquipment(await apiFetch<Equipment[]>('/api/equipment'))
    } catch {
      /* 忽略 */
    }
  }

  useEffect(() => {
    loadStandards('')
    loadEquipment()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const setItem = (key: number, patch: Partial<ItemRow>) =>
    setItems((prev) => prev.map((i) => (i.key === key ? { ...i, ...patch } : i)))

  const openStdModal = (target: 'create' | Standard) => {
    stdForm.resetFields()
    if (target === 'create') {
      setItems([{ key: rowKey++, name: '', category: 'EMI', method: '', criteria: '' }])
    } else {
      stdForm.setFieldsValue({
        std_no: target.std_no,
        name: target.name,
        effective_date: target.effective_date,
        status: target.status,
      })
      setItems(
        target.items.map((i) => ({
          key: rowKey++,
          name: i.name,
          category: i.category as 'EMI' | 'EMS',
          method: i.method ?? '',
          criteria: i.criteria ?? '',
        })),
      )
    }
    setStdModal(target)
  }

  const submitStd = async () => {
    const values = await stdForm.validateFields()
    const clean = items.filter((i) => i.name.trim())
    if (clean.length === 0) {
      message.warning('请至少填写一个测试项目')
      return
    }
    setBusy(true)
    try {
      const payload = {
        std_no: values.std_no,
        name: values.name,
        effective_date: values.effective_date || null,
        status: values.status ?? 'active',
        items: clean.map(({ key: _k, ...rest }) => rest),
      }
      if (stdModal === 'create') {
        await apiFetch<Standard>('/api/standards', { method: 'POST', body: JSON.stringify(payload) })
        message.success('标准已入库')
      } else if (stdModal) {
        await apiFetch<Standard>(`/api/standards/${stdModal.id}`, { method: 'PUT', body: JSON.stringify(payload) })
        message.success('标准已更新')
      }
      setStdModal(null)
      loadStandards(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const delStd = async (s: Standard) => {
    try {
      await apiFetch(`/api/standards/${s.id}`, { method: 'DELETE' })
      message.success('标准已删除')
      if (detail?.id === s.id) setDetail(null)
      loadStandards(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '删除失败')
    }
  }

  const submitEq = async () => {
    const values = await eqForm.validateFields()
    setBusy(true)
    try {
      if (eqModal === 'create') {
        await apiFetch<Equipment>('/api/equipment', { method: 'POST', body: JSON.stringify(values) })
        message.success('设备已登记')
      } else if (eqModal) {
        await apiFetch<Equipment>(`/api/equipment/${eqModal.id}`, { method: 'PUT', body: JSON.stringify(values) })
        message.success('设备已更新')
      }
      setEqModal(null)
      loadEquipment()
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const delEq = async (e: Equipment) => {
    try {
      await apiFetch(`/api/equipment/${e.id}`, { method: 'DELETE' })
      message.success('设备已删除')
      loadEquipment()
    } catch (err) {
      message.error(err instanceof Error ? err.message : '删除失败')
    }
  }

  const stdColumns: ColumnsType<Standard> = [
    { title: '标准号', dataIndex: 'std_no', width: 160, render: (v: string) => <span className="cust-code">{v}</span> },
    {
      title: '名称',
      dataIndex: 'name',
      render: (v: string) => <span className="cust-name">{v}</span>,
    },
    { title: '项目数', dataIndex: 'item_count', width: 90, align: 'right' },
    {
      title: '状态',
      dataIndex: 'status',
      width: 90,
      render: (v: string) => (v === 'active' ? <Tag color="green">现行</Tag> : <Tag>废止</Tag>),
    },
    {
      title: '生效日期',
      dataIndex: 'effective_date',
      width: 110,
      render: (v: string | null) => (v ? <span className="cust-date">{v}</span> : '—'),
    },
    {
      title: '',
      width: isAdmin ? 130 : 80,
      render: (_, r) => (
        <span>
          <Button type="link" size="small" onClick={() => setDetail(r)}>
            详情
          </Button>
          {isAdmin && (
            <>
              <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openStdModal(r)} />
              <Popconfirm title={`删除 ${r.std_no} 及其项目？`} onConfirm={() => delStd(r)} okText="删除" cancelText="取消">
                <Button type="link" size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </>
          )}
        </span>
      ),
    },
  ]

  const eqColumns: ColumnsType<Equipment> = [
    { title: '编号', dataIndex: 'code', width: 110, render: (v: string) => <span className="cust-code">{v}</span> },
    { title: '名称', dataIndex: 'name' },
    { title: '型号', dataIndex: 'model', width: 140, render: (v: string | null) => v ?? '—' },
    { title: '位置', dataIndex: 'location', width: 140, render: (v: string | null) => v ?? '—' },
    {
      title: '',
      width: isAdmin ? 100 : 0,
      render: (_, r) =>
        isAdmin ? (
          <span>
            <Button
              type="link"
              size="small"
              icon={<EditOutlined />}
              onClick={() => {
                eqForm.setFieldsValue(r)
                setEqModal(r)
              }}
            />
            <Popconfirm title={`删除 ${r.name}？`} onConfirm={() => delEq(r)} okText="删除" cancelText="取消">
              <Button type="link" size="small" danger icon={<DeleteOutlined />} />
            </Popconfirm>
          </span>
        ) : null,
    },
  ]

  return (
    <>
      <div className="page-head">
        <h3>标准库</h3>
        <span className="count">
          {tab === 'standards' ? `${standards.length} 项标准` : `${equipment.length} 台设备`}
        </span>
        {tab === 'standards' && (
          <div className="search">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
              <circle cx="11" cy="11" r="6.5" />
              <path d="m20 20-4.3-4.3" />
            </svg>
            <input placeholder="搜索标准号 / 名称…" value={q} onChange={(e) => { setQ(e.target.value); loadStandards(e.target.value) }} />
          </div>
        )}
        {isAdmin && tab === 'standards' && (
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => openStdModal('create')}>
            入库标准
          </Button>
        )}
        {isAdmin && tab === 'equipment' && (
          <Button
            type="primary"
            size="large"
            icon={<PlusOutlined />}
            onClick={() => {
              eqForm.resetFields()
              setEqModal('create')
            }}
          >
            登记设备
          </Button>
        )}
      </div>

      <div className="customers-panel stagger">
        <Tabs
          activeKey={tab}
          onChange={setTab}
          items={[
            { key: 'standards', label: '标准与项目' },
            { key: 'equipment', label: '设备' },
          ]}
        />
        {tab === 'standards' ? (
          <Table
            rowKey="id"
            columns={stdColumns}
            dataSource={standards}
            loading={loading}
            pagination={false}
            size="middle"
            onRow={(r) => ({ onClick: () => setDetail(r), style: { cursor: 'pointer' } })}
            locale={{
              emptyText: (
                <div className="empty-invite">
                  <b>标准库还是空的</b>
                  <p>录入官方标准（如 GB 9254-2028）与测试项目，任务与报告都从这里取判据</p>
                  {isAdmin && (
                    <Button type="primary" icon={<PlusOutlined />} onClick={() => openStdModal('create')}>
                      入库第一个标准
                    </Button>
                  )}
                </div>
              ),
            }}
          />
        ) : (
          <Table
            rowKey="id"
            columns={eqColumns}
            dataSource={equipment}
            pagination={false}
            size="middle"
            locale={{ emptyText: <div className="empty-invite"><b>还没有设备</b><p>登记测试设备后，排程可以按设备安排任务</p></div> }}
          />
        )}
      </div>

      {/* 标准详情 Drawer */}
      <Drawer
        open={detail !== null}
        onClose={() => setDetail(null)}
        width={640}
        title={
          detail && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="cust-code" style={{ fontSize: 15 }}>{detail.std_no}</span>
              {detail.status === 'active' ? <Tag color="green">现行</Tag> : <Tag>废止</Tag>}
            </span>
          )
        }
        extra={
          isAdmin && detail && (
            <Button icon={<EditOutlined />} onClick={() => openStdModal(detail)}>
              编辑
            </Button>
          )
        }
      >
        {detail && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 18 }}>
              <Descriptions.Item label="名称" span={2}>{detail.name}</Descriptions.Item>
              <Descriptions.Item label="生效日期">{detail.effective_date ?? '—'}</Descriptions.Item>
              <Descriptions.Item label="项目数">{detail.item_count}</Descriptions.Item>
            </Descriptions>
            <Table
              rowKey="id"
              size="small"
              pagination={false}
              dataSource={detail.items}
              columns={[
                { title: '项目', dataIndex: 'name' },
                {
                  title: '类别',
                  dataIndex: 'category',
                  width: 80,
                  render: (v: string) => (
                    <Tag color={v === 'EMI' ? 'blue' : 'purple'}>{v}</Tag>
                  ),
                },
                { title: '方法', dataIndex: 'method', width: 160, render: (v: string | null) => v ?? '—' },
                { title: '判据', dataIndex: 'criteria', render: (v: string | null) => v ?? '—' },
              ]}
            />
          </>
        )}
      </Drawer>

      {/* 标准 Modal */}
      <Modal
        open={stdModal !== null}
        title={stdModal === 'create' ? '入库标准' : `编辑 ${stdModal?.std_no ?? ''}`}
        width={820}
        onCancel={() => setStdModal(null)}
        onOk={submitStd}
        okText={stdModal === 'create' ? '入库' : '保存'}
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={stdForm} layout="vertical" style={{ marginTop: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
            <Form.Item name="std_no" label="官方标准号" rules={[{ required: true, message: '如 GB 9254-2028' }]}>
              <Input placeholder="GB 9254-2028" />
            </Form.Item>
            <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入标准名称' }]}>
              <Input placeholder="信息技术设备的无线电骚扰限值和测量方法" />
            </Form.Item>
            <Form.Item name="status" label="状态" initialValue="active">
              <Select options={[{ value: 'active', label: '现行' }, { value: 'obsolete', label: '废止' }]} />
            </Form.Item>
          </div>
          <Form.Item name="effective_date" label="生效日期（选填）">
            <Input placeholder="YYYY-MM-DD" style={{ width: 200 }} />
          </Form.Item>

          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '4px 0 10px' }}>测试项目</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 90px 1fr 1.2fr 36px', gap: 8, marginBottom: 6, fontSize: 11.5, color: 'var(--ink3)', fontWeight: 600 }}>
            <span>项目名称</span><span>类别</span><span>方法</span><span>判据</span><span />
          </div>
          {items.map((i) => (
            <div key={i.key} style={{ display: 'grid', gridTemplateColumns: '1fr 90px 1fr 1.2fr 36px', gap: 8, marginBottom: 8, alignItems: 'center' }}>
              <Input value={i.name} onChange={(e) => setItem(i.key, { name: e.target.value })} placeholder="如：辐射发射" />
              <Select
                value={i.category}
                onChange={(v) => setItem(i.key, { category: v })}
                options={[{ value: 'EMI', label: 'EMI' }, { value: 'EMS', label: 'EMS' }]}
              />
              <Input value={i.method} onChange={(e) => setItem(i.key, { method: e.target.value })} placeholder="如：30m 开阔场" />
              <Input value={i.criteria} onChange={(e) => setItem(i.key, { criteria: e.target.value })} placeholder="如：准峰值限值" />
              <Button type="text" danger icon={<DeleteOutlined />} disabled={items.length === 1} onClick={() => setItems((prev) => prev.filter((x) => x.key !== i.key))} />
            </div>
          ))}
          <Button icon={<PlusOutlined />} type="dashed" block onClick={() => setItems((prev) => [...prev, { key: rowKey++, name: '', category: 'EMI', method: '', criteria: '' }])}>
            添加项目
          </Button>
        </Form>
      </Modal>

      {/* 设备 Modal */}
      <Modal
        open={eqModal !== null}
        title={eqModal === 'create' ? '登记设备' : `编辑 ${eqModal?.name ?? ''}`}
        width={480}
        onCancel={() => setEqModal(null)}
        onOk={submitEq}
        okText={eqModal === 'create' ? '登记' : '保存'}
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={eqForm} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="name" label="名称" rules={[{ required: true, message: '请输入设备名称' }]}>
            <Input placeholder="如：频谱分析仪" />
          </Form.Item>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <Form.Item name="model" label="型号">
              <Input placeholder="如：FSN5071A" />
            </Form.Item>
            <Form.Item name="location" label="位置">
              <Input placeholder="如：屏蔽室 A" />
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </>
  )
}
