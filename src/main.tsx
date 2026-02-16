import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import Auth from './auth/Auth'
import API from './api/API'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Auth>
      <API>
        <App />
      </API>
    </Auth>
  </StrictMode>,
)
