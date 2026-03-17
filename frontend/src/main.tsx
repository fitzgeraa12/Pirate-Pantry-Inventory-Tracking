import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { API } from './API'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import RequireAuth from './auth/RequireAuth'
import AuthCallback from './auth/AuthCallback'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <API.Component>
      <BrowserRouter>
        <Routes>
          <Route path="/auth/callback" element={<AuthCallback />} />
          <Route path="*" element={
            <RequireAuth>
              <App />
            </RequireAuth>
          } />
        </Routes>
      </BrowserRouter>
    </API.Component>
  </StrictMode>
)
