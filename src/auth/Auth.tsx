import { GoogleLogin, GoogleOAuthProvider, type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { useEffect, useState, type PropsWithChildren } from 'react';
import { AuthContext } from './AuthContext';

const CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";
const AUTH_TITLE = "Pirate Pantry - Login"
const SU_DOMAIN = "southwestern.edu"

function Auth({ children }: PropsWithChildren) {
    const [auth, set_auth] = useState<string | null>(null);

    // Runs once at start
    useEffect(() => {
        document.title = AUTH_TITLE;
    }, [])

    const on_success = (res: CredentialResponse) => {
        try {
            const creds_encoded = res.credential!;
            const creds = jwtDecode<{ email: string }>(creds_encoded);

            if (!creds.email.endsWith(SU_DOMAIN)) {
                console.error("Unauthorized email domain");
                return;
            }

            console.log(creds_encoded);
            set_auth(creds_encoded);
        } catch (_) {
            console.error("Failed to parse credentials response");
        }
    }

    const on_error = () => {
        console.error("Login failed");
    }

    return auth ? (
        <AuthContext value={auth}>
            {children}
        </AuthContext>
    ) : (
        <GoogleOAuthProvider clientId={CLIENT_ID}>
            <GoogleLogin onSuccess={on_success} onError={on_error} hosted_domain={SU_DOMAIN}></GoogleLogin>
        </GoogleOAuthProvider>
    );
}

export default Auth;