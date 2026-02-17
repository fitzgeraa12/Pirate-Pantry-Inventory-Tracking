import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import Auth from './auth/Auth'
import API from './api/API'
import { BrowserRouter } from 'react-router-dom'
import Perms from './auth/perms/Perms'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Auth>
        <API>
          <Perms>
            <App />
          </Perms>
        </API>
      </Auth>
    </BrowserRouter>
  </StrictMode>
)
