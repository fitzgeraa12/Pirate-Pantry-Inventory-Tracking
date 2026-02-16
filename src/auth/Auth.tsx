import {GoogleLogin, GoogleOAuthProvider, type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { useEffect, useState, type PropsWithChildren } from 'react';
import { AuthContext } from './AuthContext';
import { Cookies } from 'typescript-cookie';

const CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";
const AUTH_TITLE = "Pirate Pantry - Login"
const SU_DOMAIN = "southwestern.edu"

// https://www.npmjs.com/package/typescript-cookie
// https://stackoverflow.com/questions/62426269/double-double-questionmarks-in-typescript
// https://www.spguides.com/typescript-compare-strings/
function Auth({ children }: PropsWithChildren) {
    const [auth, set_auth] = useState<string | null>(() => {
        const cookie = Cookies.get("auth");
        if (typeof(cookie) !== "string") {
            console.error("Invalid auth cookie");
            return null;
        }

        return cookie;
    });

    // Runs once at start
    useEffect(() => {
        document.title = AUTH_TITLE;
    }, [])

    const on_success = (res: CredentialResponse) => {
        try {
            const creds_encoded = res.credential!;
            const creds = jwtDecode<{ email: string }>(creds_encoded);

            if (!creds.email.endsWith(SU_DOMAIN)) {
                console.warn("Unauthorized email");
                return;
            }

            Cookies.set("auth", creds_encoded, { expires: 1 });
            set_auth(creds_encoded);
        } catch (_) {
            console.error("Failed to parse credentials response");
        }
    }

    const on_error = () => {
        console.error("Authentication failed")
    }

    if (!auth) return (
        <GoogleOAuthProvider clientId={CLIENT_ID}>
            <GoogleLogin onSuccess={on_success} onError={on_error} />
        </GoogleOAuthProvider>
    );

    return (
        <AuthContext value={auth }>
            {children}
        </AuthContext>
    );
}

export default Auth;