import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { GoogleOAuthProvider } from '@react-oauth/google';
import { StrictMode } from 'react';

const CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <GoogleOAuthProvider clientId={CLIENT_ID}>
            <App />
        </GoogleOAuthProvider>
    </StrictMode>
)
