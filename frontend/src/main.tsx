import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import AuthProvider from './auth/Auth'
import APIProvider from './api/API'
import { BrowserRouter } from 'react-router-dom'
import { CartProvider } from './misc/CartContext'
import PermsProvider from './auth/perms/Perms'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <CartProvider>
        <AuthProvider>
          <APIProvider>
            <PermsProvider>
              <App />
            </PermsProvider>
          </APIProvider>
        </AuthProvider>
      </CartProvider>
    </BrowserRouter>
  </StrictMode>
)
