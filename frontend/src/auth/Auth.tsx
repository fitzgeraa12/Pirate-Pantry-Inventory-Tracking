import { googleLogout, type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import { useContext, useEffect, useState, type PropsWithChildren } from 'react';
import { AuthContext } from './AuthContext';
import { Cookies } from 'typescript-cookie';
import Login from './Login';
import { APIContext } from '../api/APIContext';
import { Option } from '../misc/misc';

const SU_DOMAIN = "southwestern.edu"

// https://www.npmjs.com/package/typescript-cookie
// https://stackoverflow.com/questions/62426269/double-double-questionmarks-in-typescript
// https://www.spguides.com/typescript-compare-strings/
function AuthProvider({ children }: PropsWithChildren) {
    const api = useContext(APIContext);
    useEffect(() => {
        if (api.is_none()) return;

        api.unwrap().cache_auth().then((cache_res) => {
            if (!cache_res) console.error("Failed to cache auth token");
        }).catch(console.error);
    }, [api])

    const [auth, set_auth] = useState<Option<string>>(() => {
        const cookie = Cookies.get("auth");
        if (typeof cookie !== "string") {
            return Option.none();
        }
        return Option.some(cookie);
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
            set_auth(Option.some(creds_encoded));
        } catch (_) {
            console.error("Failed to parse credentials response");
        }
    }

    const on_error = () => {
        console.error("Authentication failed")
    }

    const logout = () => {
        googleLogout();
        Cookies.remove("auth");
        set_auth(Option.none());
    };

    return auth.into_inner() ? (
        <Login on_success={on_success} on_error={on_error}/>
    ) : (
        <AuthContext value={Option.some({token: auth.unwrap(), logout})}>
            {children}
        </AuthContext>
    );
}

export default AuthProvider;