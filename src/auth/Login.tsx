import { GoogleLogin, googleLogout, GoogleOAuthProvider, type CredentialResponse } from "@react-oauth/google";
import Titled from "../misc/Titled";

const CLIENT_ID = "391677624577-24ihed14clpj1d3ioumsq08aeagrj30n.apps.googleusercontent.com";

interface LoginInterface {
    on_success: (res: CredentialResponse) => void,
    on_error: () => void,
    on_logout?: () => void,
}

function Login({ on_success, on_error, on_logout }: LoginInterface) {
    const handleLogout = () => {
        googleLogout();
        localStorage.removeItem("token");
        on_logout?.();
    };
    return (
        <Titled title="Login">
            <GoogleOAuthProvider clientId={CLIENT_ID}>
                <GoogleLogin onSuccess={on_success} onError={on_error} />
            </GoogleOAuthProvider>
        </Titled>
    );
}



export default Login;
