import { useState } from 'react'
import { Form, Input, Button, Card, App as AntApp } from 'antd'
import { useNavigate } from 'react-router-dom'
import { apiFetch, setToken } from '../api/client'

export default function LoginPage() {
  const nav = useNavigate()
  const { message } = AntApp.useApp()
  const [busy, setBusy] = useState(false)

  const onFinish = async (v: { username: string; password: string }) => {
    setBusy(true)
    try {
      const r = await apiFetch<{ access_token: string }>('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(v),
      })
      setToken(r.access_token)
      nav('/dashboard')
    } catch (e) {
      message.error(e instanceof Error ? e.message : '登录失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: '#f0f2f5',
      }}
    >
      <Card title="LIMS 实验室信息管理系统" style={{ width: 380 }}>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input autoFocus />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true }]}>
            <Input.Password />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={busy}>
            登录
          </Button>
        </Form>
      </Card>
    </div>
  )
}
