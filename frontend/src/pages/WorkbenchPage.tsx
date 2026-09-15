import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { apiFetch } from '../api/client'
import { useMe } from '../auth'
import { dotColor } from '../theme'
import type { Customer } from '../types'

const WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六']

function greeting(h: number) {
  return h < 9 ? '早上好' : h < 12 ? '上午好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
}

const TODOS = [
  {
    code: 'QT-2026-018',
    title: '报价单待客户确认',
    sub: '华为终端 · 剩 2 天',
    tone: 'amber',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
        <path d="M6 2.8h9L20 7.8v13a1.2 1.2 0 0 1-1.2 1.2H6A1.2 1.2 0 0 1 4.8 20.8V4A1.2 1.2 0 0 1 6 2.8Z" />
        <path d="M8.5 12h7M8.5 15.5h4" />
      </svg>
    ),
  },
  {
    code: 'SM-2026-0231',
    title: '样品待安排测试',
    sub: '小米通讯',
    tone: 'blue',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2.8 20 7v10l-8 4.2L4 17V7l8-4.2Z" />
        <path d="M4 7l8 4.2L20 7" />
      </svg>
    ),
  },
  {
    code: 'EP-2026-041',
    title: '报告待审核',
    sub: '立讯精密',
    tone: 'teal',
    icon: (
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="8.5" />
        <path d="m8.5 12.2 2.4 2.4 4.6-4.8" />
      </svg>
    ),
  },
] as const

const TONE: Record<string, { bg: string; fg: string }> = {
  amber: { bg: 'var(--amber-soft)', fg: 'var(--amber)' },
  blue: { bg: 'var(--signal-soft)', fg: 'var(--signal)' },
  teal: { bg: 'var(--trace-soft)', fg: 'var(--trace)' },
}

const Plus = (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
    <path d="M12 5v14M5 12h14" />
  </svg>
)

export default function WorkbenchPage() {
  const nav = useNavigate()
  const me = useMe()
  const [recent, setRecent] = useState<Customer[] | null>(null)
  const [noPerm, setNoPerm] = useState(false)
  const now = new Date()

  useEffect(() => {
    if (me?.role === 'engineer') return // 工程师对客户模块无权限
    apiFetch<Customer[]>('/api/customers?limit=5')
      .then((cs) => setRecent(cs.slice(0, 5)))
      .catch(() => setNoPerm(true))
  }, [me?.role])

  const dateStr = `${now.getFullYear()}.${String(now.getMonth() + 1).padStart(2, '0')}.${String(
    now.getDate(),
  ).padStart(2, '0')} 周${WEEKDAYS[now.getDay()]}`

  return (
    <>
      <div className="greet">
        <h3>
          {greeting(now.getHours())}，{me?.name}
        </h3>
        <span>
          {dateStr} · {TODOS.length} 项待办
        </span>
      </div>

      <div className="actions stagger">
        {me?.role !== 'engineer' && (
          <div className="act primary" onClick={() => nav('/customers', { state: { create: true } })}>
            {Plus}
            新建客户
          </div>
        )}
        {me?.role === 'business' && (
          <div className="act ghost" onClick={() => nav('/quotations', { state: { create: true } })}>
            {Plus}
            新建报价
          </div>
        )}
        <div
          className="act ghost"
          onClick={() => nav('/entrustments', { state: { create: me?.role !== 'engineer' } })}
        >
          {Plus}
          新建委托
        </div>
        <div className="act soon">
          更多模块<em>按角色逐步开放</em>
        </div>
      </div>

      <div className="stats stagger">
        <div className="stat">
          <div className="k">
            本月委托 <span className="demo">示例</span>
          </div>
          <div className="v">
            12<small>单</small>
          </div>
          <div className="d">
            较上月 <b className="up">+3</b>
          </div>
        </div>
        <div className="stat">
          <div className="k">
            在测样品 <span className="demo">示例</span>
          </div>
          <div className="v">
            5<small>件</small>
          </div>
          <div className="d">2 件今日到期</div>
        </div>
        <div className="stat">
          <div className="k">
            待出报告 <span className="demo">示例</span>
          </div>
          <div className="v">
            3<small>份</small>
          </div>
          <div className="d">最早 09-16 交付</div>
        </div>
      </div>

      <div className="cols stagger">
        <div className="panel">
          <div className="head">
            <b>最近客户</b>
            {me?.role !== 'engineer' && (
              <a onClick={() => nav('/customers')}>查看全部 →</a>
            )}
          </div>
          {noPerm ? (
            <div className="empty-invite" style={{ padding: '36px 24px' }}>
              <p style={{ margin: 0 }}>该视图对当前角色不可见</p>
            </div>
          ) : recent && recent.length > 0 ? (
            <>
              <div className="row h">
                <span>客户</span>
                <span>编号</span>
                <span>行业</span>
                <span>建档</span>
              </div>
              {recent.map((c) => (
                <div key={c.id} className="row" style={{ cursor: 'pointer' }} onClick={() => nav('/customers')}>
                  <span className="cname">
                    <i className="dot" style={{ background: dotColor(c.name) }} />
                    {c.name}
                  </span>
                  <span className="code">{c.code}</span>
                  <span>{c.industry ?? '—'}</span>
                  <span className="date">{c.created_at.slice(5, 10)}</span>
                </div>
              ))}
            </>
          ) : (
            <div className="empty-invite" style={{ padding: '36px 24px' }}>
              <p style={{ margin: 0 }}>还没有客户 —— 建档后即可发起报价与委托</p>
            </div>
          )}
        </div>
        <div className="panel">
          <div className="head">
            <b>
              待办 <span className="demo" style={{ fontSize: 10, color: 'var(--ink3)', background: '#F1F4F8', borderRadius: 99, padding: '1.5px 7px', marginLeft: 8 }}>示例</span>
            </b>
            <a>全部 →</a>
          </div>
          {TODOS.map((t) => (
            <div key={t.code} className="todo" title="模块即将上线">
              <div className="ic" style={{ background: TONE[t.tone].bg, color: TONE[t.tone].fg }}>
                {t.icon}
              </div>
              <div className="tx">
                {t.title}
                <small>
                  <span className="code">{t.code}</span> · {t.sub}
                </small>
              </div>
              <div className="go">→</div>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}
