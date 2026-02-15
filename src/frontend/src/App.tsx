import { useCallback, useEffect, useState } from 'react';
import './App.css';
import AddItem from './inventory/AddItem';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';

function App() {
    const [auth_token, set_auth_token] = useState<string | null>(null);
    const [add_item_enabled, set_add_item_enabled] = useState(true);

    // https://www.npmjs.com/package/@react-oauth/google?activeTab=readme
    // https://blog.logrocket.com/guide-adding-google-login-react-app/
    const google_res = (res: CredentialResponse) => {
        set_auth_token(res.credential!);
    };
    const google_err = () => {
        console.error("Login failed");
    };

    if (!auth_token) {
        return <>
            <GoogleLogin onSuccess={google_res} onError={google_err}></GoogleLogin>
        </>
    }
    
    return (
        <>
            {add_item_enabled && <AddItem />}
        </>
    );
}

export default App;
