import type { ThemeConfig } from 'antd'

/** LIMS 设计 token（与 app.css 的 CSS 变量同源）。
 * 反传统 ERP：电蓝主色 + 示波青点缀 + 离白底大圆角。 */
export const T = {
  ink: '#16233B',
  ink2: '#5A6B85',
  ink3: '#8A99B0',
  canvas: '#F4F6F9',
  surface: '#FFFFFF',
  line: '#E7EBF1',
  signal: '#2458F5',
  signalSoft: '#EAF0FF',
  signalInk: '#1B3FAE',
  trace: '#12B98A',
  traceGlow: '#2FE3B0',
  amber: '#E8930C',
  navy: '#0B1424',
  mono: 'ui-monospace, "SF Mono", "JetBrains Mono", Consolas, monospace',
} as const

export const antdTheme: ThemeConfig = {
  token: {
    colorPrimary: T.signal,
    colorInfo: T.signal,
    colorSuccess: T.trace,
    colorWarning: T.amber,
    colorError: '#EF4444',
    colorText: T.ink,
    colorTextSecondary: T.ink2,
    colorTextTertiary: T.ink3,
    colorBorder: T.line,
    colorBorderSecondary: T.line,
    colorBgLayout: T.canvas,
    borderRadius: 10,
    fontFamily:
      '-apple-system, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Segoe UI", sans-serif',
  },
  components: {
    Button: { borderRadius: 10 },
    Input: { borderRadius: 10 },
    Select: { borderRadius: 10 },
    Modal: { borderRadiusLG: 16 },
    Tag: { borderRadiusSM: 99 },
  },
}

/** 客户色点调色板（列表/最近客户的区分色） */
export const DOT_COLORS = ['#2458F5', '#12B98A', '#E8930C', '#7C5CFC', '#E0559B', '#0EA5E9']

export function dotColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) >>> 0
  return DOT_COLORS[h % DOT_COLORS.length]
}
