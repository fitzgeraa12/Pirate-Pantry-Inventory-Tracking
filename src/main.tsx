import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import Auth from './auth/Auth'
import API from './api/API'
import { BrowserRouter } from 'react-router-dom'
import Perms from './auth/perms/Perms'
import { CartProvider } from './misc/CartContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <CartProvider>
        <Auth>
          <API>
            <Perms>
              <App />
            </Perms>
          </API>
        </Auth>
      </CartProvider>
    </BrowserRouter>
  </StrictMode>
)
