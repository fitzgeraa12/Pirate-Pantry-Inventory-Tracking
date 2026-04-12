import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { API } from './API'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import RequireAuth from './auth/RequireAuth'
import AuthCallback from './auth/AuthCallback'
import Unauthorized from './auth/Unauthorized'
import { CartProvider } from './misc/CartContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <API.Component>
      <CartProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/auth/unauthorized" element={<Unauthorized />} />
            <Route path="*" element={
              <RequireAuth>
                <App />
              </RequireAuth>
            } />
          </Routes>
        </BrowserRouter>
      </CartProvider>  
    </API.Component>
  </StrictMode>
)
