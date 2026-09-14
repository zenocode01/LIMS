import { useState } from 'react'
import { Form, Input, Button, App as AntApp } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
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
      nav('/', { replace: true })
    } catch (e) {
      message.error(e instanceof Error ? e.message : '登录失败')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-grid" />
      <div className="login-wave">
        <svg viewBox="0 0 1440 220" preserveAspectRatio="none">
          <path
            d="M0 110 H240 V58 H380 V150 H520 V110 H700 V84 H840 V142 H980 V110 H1180 V66 H1320 V110 H1440"
            fill="none"
            stroke="#2FE3B0"
            strokeWidth="2.4"
            opacity="0.85"
            pathLength={1}
            className="trace-path"
          />
        </svg>
      </div>
      <div className="login-brand">
        <div className="eyebrow">EMC · ELECTROMAGNETIC COMPATIBILITY</div>
        <h1>
          LIMS <small>v0.2</small>
        </h1>
        <div className="rule" />
        <p>电磁兼容实验室 · 信息工作台</p>
      </div>
      <div className="login-card">
        <h2>登录工作台</h2>
        <div className="sub">使用分配的账号进入本实验室系统</div>
        <Form layout="vertical" onFinish={onFinish}>
          <Form.Item name="username" label="用户名" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="请输入用户名" autoFocus size="large" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="请输入密码" size="large" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block size="large" loading={busy} style={{ marginTop: 8 }}>
            登 录
          </Button>
        </Form>
        <div className="note">
          <span>受控环境 · 请勿外传账号</span>
          <b>LIMS WORKBENCH</b>
        </div>
      </div>
      <div className="login-foot">本地部署 · 内网访问</div>
    </div>
  )
}
