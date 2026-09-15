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
  Switch,
  Table,
  Tag,
  App as AntApp,
} from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import type { RecordTemplate } from '../types'

interface FieldRow {
  key: number
  field_name: string
  field_type: string
  unit: string
  required: boolean
  criteria_expr: string
}

const LEVEL_LABELS: Record<number, string> = {
  1: '手册',
  2: '程序文件',
  3: '作业指导书',
  4: '纯记录表单',
}
const CONTROLLED_TAG: Record<string, { color: string; label: string }> = {
  draft: { color: 'default', label: '未受控' },
  controlled: { color: 'green', label: '受控' },
  obsolete: { color: 'red', label: '作废' },
}

let rowKey = 0

export default function TemplatesPage() {
  const me = useMe()
  const isAdmin = me?.role === 'admin'
  const { message } = AntApp.useApp()

  const [rows, setRows] = useState<RecordTemplate[]>([])
  const [q, setQ] = useState('')
  const [loading, setLoading] = useState(false)
  const [detail, setDetail] = useState<RecordTemplate | null>(null)
  const [modal, setModal] = useState<'create' | RecordTemplate | null>(null)
  const [fields, setFields] = useState<FieldRow[]>([])
  const [busy, setBusy] = useState(false)
  const [form] = Form.useForm()

  const load = async (query: string) => {
    setLoading(true)
    try {
      const url = `/api/record-templates${query.trim() ? `?q=${encodeURIComponent(query.trim())}` : ''}`
      setRows(await apiFetch<RecordTemplate[]>(url))
    } catch (e) {
      message.error(e instanceof Error ? e.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load('')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const setField = (key: number, patch: Partial<FieldRow>) =>
    setFields((prev) => prev.map((f) => (f.key === key ? { ...f, ...patch } : f)))

  const openModal = (target: 'create' | RecordTemplate) => {
    form.resetFields()
    if (target === 'create') {
      setFields([{ key: rowKey++, field_name: '', field_type: 'text', unit: '', required: false, criteria_expr: '' }])
    } else {
      form.setFieldsValue({
        name: target.name,
        form_level: target.form_level,
        category: target.category,
        controlled: target.controlled,
        version: target.version,
      })
      setFields(
        target.fields.map((f) => ({
          key: rowKey++,
          field_name: f.field_name,
          field_type: f.field_type,
          unit: f.unit ?? '',
          required: f.required,
          criteria_expr: f.criteria_expr ?? '',
        })),
      )
    }
    setModal(target)
  }

  const submit = async () => {
    const values = await form.validateFields()
    const clean = fields.filter((f) => f.field_name.trim())
    if (clean.length === 0) {
      message.warning('请至少定义一个字段')
      return
    }
    setBusy(true)
    try {
      const payload = {
        ...values,
        fields: clean.map(({ key: _k, ...rest }) => rest),
      }
      if (modal === 'create') {
        await apiFetch<RecordTemplate>('/api/record-templates', { method: 'POST', body: JSON.stringify(payload) })
        message.success('模板已创建')
      } else if (modal) {
        await apiFetch<RecordTemplate>(`/api/record-templates/${modal.id}`, { method: 'PUT', body: JSON.stringify(payload) })
        message.success('模板已更新')
      }
      setModal(null)
      load(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '保存失败')
    } finally {
      setBusy(false)
    }
  }

  const del = async (t: RecordTemplate) => {
    try {
      await apiFetch(`/api/record-templates/${t.id}`, { method: 'DELETE' })
      message.success('模板已删除')
      if (detail?.id === t.id) setDetail(null)
      load(q)
    } catch (e) {
      message.error(e instanceof Error ? e.message : '删除失败')
    }
  }

  const columns: ColumnsType<RecordTemplate> = [
    { title: '模板号', dataIndex: 'tpl_no', width: 90, render: (v: string) => <span className="cust-code">{v}</span> },
    { title: '名称', dataIndex: 'name', render: (v: string) => <span className="cust-name">{v}</span> },
    { title: '表单层级', dataIndex: 'form_level', width: 110, render: (v: number) => LEVEL_LABELS[v] ?? v },
    {
      title: '类别',
      dataIndex: 'category',
      width: 90,
      render: (v: string) => (
        <Tag color={v === 'EMI' ? 'blue' : v === 'EMS' ? 'purple' : 'default'}>{v}</Tag>
      ),
    },
    {
      title: '受控',
      dataIndex: 'controlled',
      width: 90,
      render: (v: string) => {
        const c = CONTROLLED_TAG[v] ?? { color: 'default', label: v }
        return <Tag color={c.color}>{c.label}</Tag>
      },
    },
    { title: '版本', dataIndex: 'version', width: 70, align: 'right', render: (v: number) => `v${v}` },
    { title: '字段数', dataIndex: 'field_count', width: 80, align: 'right' },
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
              <Button type="link" size="small" icon={<EditOutlined />} onClick={() => openModal(r)} />
              <Popconfirm title={`删除模板 ${r.tpl_no}？`} onConfirm={() => del(r)} okText="删除" cancelText="取消">
                <Button type="link" size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </>
          )}
        </span>
      ),
    },
  ]

  return (
    <>
      <div className="page-head">
        <h3>记录模板</h3>
        <span className="count">{rows.length} 份</span>
        <div className="search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m20 20-4.3-4.3" />
          </svg>
          <input placeholder="搜索模板号 / 名称…" value={q} onChange={(e) => { setQ(e.target.value); load(e.target.value) }} />
        </div>
        {isAdmin && (
          <Button type="primary" size="large" icon={<PlusOutlined />} onClick={() => openModal('create')}>
            新建模板
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
                <b>模板库还是空的</b>
                <p>模板=字段定义：一次投入，长期复用 —— 原始记录按模板结构化录入</p>
                {isAdmin && (
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal('create')}>
                    建第一份模板
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
        width={680}
        title={
          detail && (
            <span style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="cust-code" style={{ fontSize: 15 }}>{detail.tpl_no}</span>
              <Tag color={CONTROLLED_TAG[detail.controlled]?.color}>{CONTROLLED_TAG[detail.controlled]?.label}</Tag>
              <span className="cust-date">v{detail.version}</span>
            </span>
          )
        }
        extra={
          isAdmin && detail && (
            <Button icon={<EditOutlined />} onClick={() => openModal(detail)}>
              编辑
            </Button>
          )
        }
      >
        {detail && (
          <>
            <Descriptions column={2} size="small" style={{ marginBottom: 18 }}>
              <Descriptions.Item label="名称" span={2}>{detail.name}</Descriptions.Item>
              <Descriptions.Item label="表单层级">{detail.form_level_label}</Descriptions.Item>
              <Descriptions.Item label="类别">{detail.category}</Descriptions.Item>
            </Descriptions>
            <Table
              rowKey="id"
              size="small"
              pagination={false}
              dataSource={detail.fields}
              columns={[
                { title: '#', dataIndex: 'field_no', width: 44, align: 'right' },
                { title: '字段', dataIndex: 'field_name', render: (v: string, r) => (r.required ? <b>{v}</b> : v) },
                { title: '类型', dataIndex: 'field_type', width: 80 },
                { title: '单位', dataIndex: 'unit', width: 80, render: (v: string | null) => v ?? '—' },
                { title: '判据表达式', dataIndex: 'criteria_expr', render: (v: string | null) => (v ? <span className="cust-code">{v}</span> : '—') },
              ]}
            />
          </>
        )}
      </Drawer>

      {/* 新建/编辑 Modal */}
      <Modal
        open={modal !== null}
        title={modal === 'create' ? '新建记录模板' : `编辑模板 ${modal?.tpl_no ?? ''}`}
        width={860}
        onCancel={() => setModal(null)}
        onOk={submit}
        okText={modal === 'create' ? '创建' : '保存'}
        cancelText="取消"
        confirmLoading={busy}
        destroyOnHidden
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: 12 }}>
            <Form.Item name="name" label="模板名称" rules={[{ required: true, message: '请输入模板名称' }]}>
              <Input placeholder="如：辐射发射记录表" />
            </Form.Item>
            <Form.Item name="form_level" label="表单层级" initialValue={4}>
              <Select
                options={Object.entries(LEVEL_LABELS).map(([v, l]) => ({ value: Number(v), label: `${v} ${l}` }))}
              />
            </Form.Item>
            <Form.Item name="category" label="类别" initialValue="EMI">
              <Select options={[{ value: 'EMI', label: 'EMI' }, { value: 'EMS', label: 'EMS' }, { value: 'common', label: '通用' }]} />
            </Form.Item>
            <Form.Item name="controlled" label="受控状态" initialValue="draft">
              <Select
                options={[
                  { value: 'draft', label: '未受控' },
                  { value: 'controlled', label: '受控' },
                  { value: 'obsolete', label: '作废' },
                ]}
              />
            </Form.Item>
          </div>

          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink2)', margin: '4px 0 10px' }}>字段定义</div>
          <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 100px 80px 64px 1.4fr 36px', gap: 8, marginBottom: 6, fontSize: 11.5, color: 'var(--ink3)', fontWeight: 600 }}>
            <span>字段名</span><span>类型</span><span>单位</span><span>必填</span><span>判据表达式</span><span />
          </div>
          {fields.map((f) => (
            <div key={f.key} style={{ display: 'grid', gridTemplateColumns: '1.2fr 100px 80px 64px 1.4fr 36px', gap: 8, marginBottom: 8, alignItems: 'center' }}>
              <Input value={f.field_name} onChange={(e) => setField(f.key, { field_name: e.target.value })} placeholder="如：峰值读数" />
              <Select
                value={f.field_type}
                onChange={(v) => setField(f.key, { field_type: v })}
                options={[
                  { value: 'text', label: '文本' },
                  { value: 'number', label: '数值' },
                  { value: 'date', label: '日期' },
                  { value: 'select', label: '选项' },
                ]}
              />
              <Input value={f.unit} onChange={(e) => setField(f.key, { unit: e.target.value })} placeholder="dBμV" />
              <Switch
                checked={f.required}
                onChange={(v) => setField(f.key, { required: v })}
                style={{ marginLeft: 16 }}
              />
              <Input value={f.criteria_expr} onChange={(e) => setField(f.key, { criteria_expr: e.target.value })} placeholder="如：<= limit" />
              <Button type="text" danger icon={<DeleteOutlined />} disabled={fields.length === 1} onClick={() => setFields((prev) => prev.filter((x) => x.key !== f.key))} />
            </div>
          ))}
          <Button icon={<PlusOutlined />} type="dashed" block onClick={() => setFields((prev) => [...prev, { key: rowKey++, field_name: '', field_type: 'text', unit: '', required: false, criteria_expr: '' }])}>
            添加字段
          </Button>
        </Form>
      </Modal>
    </>
  )
}
