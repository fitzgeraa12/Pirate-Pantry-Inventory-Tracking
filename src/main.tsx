import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import Auth from './auth/Auth'
import API from './api/API'
import { BrowserRouter } from 'react-router-dom'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Auth>
        <API>
          <App />
        </API>
      </Auth>
    </BrowserRouter>
  </StrictMode>,
)
