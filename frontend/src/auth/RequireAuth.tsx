import React from "react";
import { API, api_base } from "../API";
import { Spinner } from "../misc/misc";

export default function RequireAuth({ children }: React.PropsWithChildren): React.ReactNode {
    const [ready, setReady] = React.useState(false);

    const API_PORT = import.meta.env.VITE_API_PORT
    const API_URL = API_PORT ? `${import.meta.env.VITE_API_URL}:${API_PORT}` : import.meta.env.VITE_API_URL

    const api = React.useContext(API.Context);

    React.useEffect(() => {
        // Fallback: handle ?code= exchange here in case /auth/callback SPA
        // routing fails (e.g. Cloudflare Pages path rewriting)
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");
        if (code) {
            window.history.replaceState({}, "", window.location.pathname);
            api_base.post("/auth/exchange", { code })
                .then(({ data }) => {
                    localStorage.setItem("session", data.session);
                    if (data.picture) localStorage.setItem("user-picture", data.picture);
                    else localStorage.removeItem("user-picture");
                    setReady(true);
                })
                .catch(() => {
                    window.location.href = `${API_URL}/auth/google`;
                });
            return;
        }

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