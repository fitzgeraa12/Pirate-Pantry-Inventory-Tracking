import React from "react";
import { useNavigate } from "react-router-dom";
import { api_base } from "../API";
import { Spinner } from "../misc/misc";

export default function AuthCallback(): React.ReactNode {
    const navigate = useNavigate();
    console.log('posting to:', api_base.defaults.baseURL + '/auth/exchange');

    React.useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const code = params.get("code");

        if (code) {
        window.history.replaceState({}, "", "/auth/callback");
        api_base.post("/auth/exchange", { code }).then(({ data }) => {
            localStorage.setItem("session", data.session);
            if (data.picture) localStorage.setItem("user-picture", data.picture);
            else localStorage.removeItem("user-picture");
            navigate("/");
        }).catch((err) => {
            console.error("Auth exchange failed:", err);
            navigate("/auth/unauthorized");
        });
        }
    }, []);

    return (
        <div className="page-loading">
            <div className="page-loading-title">Pirate Pantry</div>
            <Spinner />
        </div>
    );
}