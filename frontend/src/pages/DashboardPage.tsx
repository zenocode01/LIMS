import { useEffect, useState } from 'react'
import { Layout, Tag, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import { apiFetch, setToken } from '../api/client'
import type { UserOut } from '../types'

const roleTag: Record<string, string> = {
  business: '业务',
  engineer: '工程师',
  admin: '管理',
}

export default function DashboardPage() {
  const nav = useNavigate()
  const [me, setMe] = useState<UserOut | null>(null)

  useEffect(() => {
    apiFetch<UserOut>('/api/auth/me')
      .then(setMe)
      .catch(() => nav('/login'))
  }, [nav])

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Layout.Header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <b>LIMS</b>
        <span>
          {me && (
            <Tag color="blue" style={{ marginRight: 8 }}>
              {roleTag[me.role]}：{me.name}
            </Tag>
          )}
          <Button size="small" onClick={() => { setToken(null); nav('/login') }}>
            退出
          </Button>
        </span>
      </Layout.Header>
      <Layout.Content style={{ padding: 24 }}>
        <p>基础底座就绪。后续模块（客户/报价/委托/样品…）见计划 P2。</p>
      </Layout.Content>
    </Layout>
  )
}
