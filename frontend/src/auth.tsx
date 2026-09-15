import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { Result, Spin } from 'antd'
import { useNavigate } from 'react-router-dom'
import { apiFetch, setToken, getToken } from './api/client'
import type { UserOut } from './types'

export const MeContext = createContext<UserOut | null>(null)
export const useMe = () => useContext(MeContext)

/** 应用外壳：拉取当前用户，按角色渲染侧栏/顶栏。
 * needRoles 用于模块级 RBAC（如客户管理：工程师无权限）。 */
export function Shell({
  children,
  needRoles,
  title,
  active,
}: {
  children: ReactNode
  needRoles?: string[]
  title: string
  active: string
}) {
  const nav = useNavigate()
  const [me, setMe] = useState<UserOut | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    if (!getToken()) {
      nav('/login', { replace: true })
      return
    }
    apiFetch<UserOut>('/api/auth/me')
      .then(setMe)
      .catch(() => setFailed(true))
  }, [nav])

  if (failed) return <Result status="403" title="403" subTitle="没有访问该模块的权限" />
  if (!me)
    return (
      <div style={{ display: 'grid', placeItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    )
  if (needRoles && !needRoles.includes(me.role))
    return (
      <Result
        status="403"
        title="403"
        subTitle={`${title}模块不对「${roleLabel(me.role)}」角色开放`}
        extra={
          <button
            className="act primary"
            style={{ margin: '0 auto' }}
            onClick={() => nav('/', { replace: true })}
          >
            返回工作台
          </button>
        }
      />
    )

  return (
    <MeContext.Provider value={me}>
      <ShellLayout me={me} title={title} active={active}>
        {children}
      </ShellLayout>
    </MeContext.Provider>
  )
}

function ShellLayout({
  me,
  title,
  active,
  children,
}: {
  me: UserOut
  title: string
  active: string
  children: ReactNode
}) {
  const nav = useNavigate()
  const items: { key: string; label: string; to: string; roles: string[] | null }[] = [
    { key: 'workbench', label: '工作台', to: '/', roles: null },
    { key: 'customers', label: '客户管理', to: '/customers', roles: ['business', 'admin'] },
    { key: 'quotations', label: '报价管理', to: '/quotations', roles: ['business', 'admin'] },
  ]
  const bizItems: { key: string; label: string; to: string; roles: string[] | null }[] = [
    { key: 'entrustments', label: '委托管理', to: '/entrustments', roles: null },
    { key: 'samples', label: '样品管理', to: '/samples', roles: null },
    { key: 'standards', label: '标准库', to: '/standards', roles: null },
    { key: 'templates', label: '记录模板', to: '/templates', roles: null },
  ]

  return (
    <div className="shell">
      <aside className="rail">
        <div className="rail-logo">
          <div className="mark">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2FE3B0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 13h5V6h5v7h5V9h5" />
            </svg>
          </div>
          <div className="name">
            LIMS
            <small>EMC LAB</small>
          </div>
        </div>
        <div className="rail-label">概览</div>
        {items
          .filter((i) => !i.roles || i.roles.includes(me.role))
          .map((i) => (
            <div
              key={i.key}
              className={`rail-item ${active === i.key ? 'on' : ''}`}
              onClick={() => nav(i.to)}
            >
              <NavIcon name={i.key} />
              {i.label}
            </div>
          ))}
        <div className="rail-label">业务</div>
        {bizItems
          .filter((i) => !i.roles || i.roles.includes(me.role))
          .map((i) => (
            <div
              key={i.key}
              className={`rail-item ${active === i.key ? 'on' : ''}`}
              onClick={() => nav(i.to)}
            >
              <NavIcon name={i.key} />
              {i.label}
            </div>
          ))}
        <div className="rail-foot">
          <div className="avatar">{me.name.slice(0, 1)}</div>
          <div className="who">
            <b>{me.name}</b>
            <span>
              {roleLabel(me.role)} · {me.username}
            </span>
          </div>
          <div
            className="out"
            title="退出登录"
            onClick={() => {
              setToken(null)
              nav('/login', { replace: true })
            }}
          >
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 4H6a1.5 1.5 0 0 0-1.5 1.5v13A1.5 1.5 0 0 0 6 20h8" />
              <path d="M10 12h10m0 0-3.2-3.2M20 12l-3.2 3.2" />
            </svg>
          </div>
        </div>
      </aside>
      <div className="shell-main">
        <div className="topbar">
          <h2>{title}</h2>
          <div className="live-badge">
            <i />
            系统运行中
          </div>
          <div className="search" title="全局搜索即将上线">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
              <circle cx="11" cy="11" r="6.5" />
              <path d="m20 20-4.3-4.3" />
            </svg>
            搜索客户 / 委托 / 报告…
            <kbd>⌘K</kbd>
          </div>
          <div className="bell" title="通知（即将上线）">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 9.5a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6" />
              <path d="M10 19.5a2.2 2.2 0 0 0 4 0" />
            </svg>
          </div>
        </div>
        <div className="shell-content">{children}</div>
      </div>
    </div>
  )
}

/** 侧栏图标（与设计稿同源的线条 SVG） */
function NavIcon({ name }: { name: string }) {
  const common = {
    width: 17,
    height: 17,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
  }
  switch (name) {
    case 'templates':
      return (
        <svg {...common}>
          <rect x="4" y="3.4" width="16" height="17.2" rx="1.4" />
          <path d="M7.5 8h9M7.5 12h9M7.5 16h5.5" />
        </svg>
      )
    case 'standards':
      return (
        <svg {...common}>
          <path d="M5 3.2h11.5L20 6.7v14a.8.8 0 0 1-.8.8H5a.8.8 0 0 1-.8-.8v-17A.8.8 0 0 1 5 3.2Z" />
          <path d="M8 3.2v4h7v-4" />
          <path d="M8 12h8M8 15.5h5" />
        </svg>
      )
    case 'samples':
      return (
        <svg {...common}>
          <path d="M12 2.8 20 7v10l-8 4.2L4 17V7Z" />
          <path d="M4 7l8 4.2L20 7M12 11.2V21" />
        </svg>
      )
    case 'entrustments':
      return (
        <svg {...common}>
          <rect x="4.8" y="4.2" width="14.4" height="17" rx="1.6" />
          <path d="M9 4.2V2.8h6v1.4" />
          <path d="m8.6 13.6 2.4 2.4 4.4-4.8" />
        </svg>
      )
    case 'quotations':
      return (
        <svg {...common}>
          <path d="M6 2.8h9L20 7.8v13a1.2 1.2 0 0 1-1.2 1.2H6A1.2 1.2 0 0 1 4.8 20.8V4A1.2 1.2 0 0 1 6 2.8Z" />
          <path d="M8.5 12h7M8.5 15.5h7M8.5 8.5h3" />
        </svg>
      )
    case 'workbench':
      return (
        <svg {...common}>
          <rect x="3" y="3" width="8" height="8" rx="2" />
          <rect x="13" y="3" width="8" height="5" rx="2" />
          <rect x="13" y="10" width="8" height="11" rx="2" />
          <rect x="3" y="13" width="8" height="8" rx="2" />
        </svg>
      )
    case 'entrustments':
      return (
        <svg {...common}>
          <rect x="5" y="4" width="14" height="17" rx="2" />
          <path d="M9 4a3 3 0 0 1 6 0M9 10h6M9 13.5h6M9 17h3.5" />
        </svg>
      )
    case 'samples':
      return (
        <svg {...common}>
          <path d="M12 2.8 20 7v10l-8 4.2L4 17V7l8-4.2Z" />
          <path d="M4 7l8 4.2L20 7M12 11.2V21" />
        </svg>
      )
    default: // customers
      return (
        <svg {...common}>
          <circle cx="9" cy="8" r="3.4" />
          <path d="M2.8 19c1.3-2.9 3.6-4.3 6.2-4.3s4.9 1.4 6.2 4.3" />
          <circle cx="17.2" cy="9.2" r="2.6" />
          <path d="M16.4 14.6c2.3.3 4 1.6 4.9 3.9" />
        </svg>
      )
  }
}

export function roleLabel(role: string): string {
  return { business: '业务', engineer: '工程师', admin: '管理' }[role] ?? role
}
