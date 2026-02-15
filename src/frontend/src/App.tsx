import { useCallback, useEffect, useState } from 'react';
import './App.css';
import AddItem from './inventory/AddItem';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';

const SU_DOMAIN = "southwestern.edu"

interface Credentials {
    email: string,
}

function App() {
    const [auth_token, set_auth_token] = useState<string | null>(null);
    const [add_item_enabled, set_add_item_enabled] = useState(true);

    // https://www.npmjs.com/package/@react-oauth/google?activeTab=readme
    // https://blog.logrocket.com/guide-adding-google-login-react-app/
    // https://stackoverflow.com/questions/53835816/decode-jwt-token-react
    const google_res = (res: CredentialResponse) => {
        try {
            const creds_encoded = res.credential!;
            const creds = jwtDecode<Credentials>(creds_encoded);

            if (!creds.email.endsWith(SU_DOMAIN)) {
                console.error("Unauthorized email domain");
                return;
            }

            set_auth_token(creds_encoded);
        } catch (_) {
            console.error("Failed to parse credentials response");
        }
    };

    const google_err = () => {
        console.error("Login failed");
    };

    if (!auth_token) {
        return <>
            <GoogleLogin
                onSuccess={google_res}
                onError={google_err}
                hosted_domain={SU_DOMAIN}
            />
        </>
    }
    
    return (
        <>
            {add_item_enabled && <AddItem />}
        </>
    );
}

export default App;
