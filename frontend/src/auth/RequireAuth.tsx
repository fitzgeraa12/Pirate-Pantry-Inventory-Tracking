import React from "react";
import { API } from "../API";
import { Spinner } from "../misc/misc";

export default function RequireAuth({ children }: React.PropsWithChildren): React.ReactNode {
    const [ready, setReady] = React.useState(false);

    const API_PORT = import.meta.env.VITE_API_PORT
    const API_URL = API_PORT ? `${import.meta.env.VITE_API_URL}:${API_PORT}` : import.meta.env.VITE_API_URL

    const api = React.useContext(API.Context);

    React.useEffect(() => {
        const session = localStorage.getItem('session');
        if (!session) {
            window.location.href = `${API_URL}/auth/google`;
            return;
        }
        
        try {
            api!.whoami().then(google_sub => {
                if (!google_sub) {
                    localStorage.removeItem('session');
                    window.location.href = `${API_URL}/auth/google`;
                } else {
                    setReady(true);
                }
            });
        } catch (error) {
            
        }
    }, []);

    if (!ready) return (
        <div className="page-loading">
            <div className="page-loading-title">Pirate Pantry</div>
            <Spinner />
        </div>
    );
    return <>{children}</>;
}