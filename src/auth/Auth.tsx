import { type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { useState, type PropsWithChildren } from 'react';
import { AuthContext } from './AuthContext';
import { Cookies } from 'typescript-cookie';
import Login from './Login';

const SU_DOMAIN = "southwestern.edu"

// https://www.npmjs.com/package/typescript-cookie
// https://stackoverflow.com/questions/62426269/double-double-questionmarks-in-typescript
// https://www.spguides.com/typescript-compare-strings/
function Auth({ children }: PropsWithChildren) {
    const [auth, set_auth] = useState<string | null>(() => {
        const cookie = Cookies.get("auth");
        if (typeof cookie !== "string") {
            console.error("Invalid auth cookie");
            return null;
        }

        return cookie;
    });

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

    return !auth ? (
        <Login on_success={on_success} on_error={on_error}></Login>
    ) : (
        <AuthContext value={auth }>
            {children}
        </AuthContext>
    );
}

export default Auth;