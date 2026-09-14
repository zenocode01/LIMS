import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { ConfigProvider, App as AntApp } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import LoginPage from './pages/LoginPage'
import WorkbenchPage from './pages/WorkbenchPage'
import CustomersPage from './pages/CustomersPage'
import QuotationsPage from './pages/QuotationsPage'
import { Shell } from './auth'
import { antdTheme } from './theme'

export default function App() {
  return (
    <ConfigProvider theme={antdTheme} locale={zhCN}>
      <AntApp>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                <Shell title="工作台" active="workbench">
                  <WorkbenchPage />
                </Shell>
              }
            />
            <Route
              path="/customers"
              element={
                <Shell title="客户管理" active="customers" needRoles={['business', 'admin']}>
                  <CustomersPage />
                </Shell>
              }
            />
            <Route
              path="/quotations"
              element={
                <Shell title="报价管理" active="quotations" needRoles={['business', 'admin']}>
                  <QuotationsPage />
                </Shell>
              }
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AntApp>
    </ConfigProvider>
  )
}
