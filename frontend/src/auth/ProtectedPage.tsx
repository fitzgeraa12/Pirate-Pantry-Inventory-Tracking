import { useCallback, type PropsWithChildren } from "react";
import React from "react";
import Unauthorized from "./Unauthorized";
import { API, type AccessLevel } from "../API";
import type { Optional } from "../misc/misc";
import { Spinner } from "../misc/misc";

interface ProtectedRouteProps {
    required_access_level: AccessLevel,
}

const ACCESS_LEVELS: AccessLevel[] = ["trusted", "admin"];

export default function ProtectedPage({ required_access_level, children }: PropsWithChildren<ProtectedRouteProps>) {
    const api = React.useContext(API.Context);
    const [has_access, set_has_access] = React.useState<Optional<boolean>>(null);

    const get_access_level = useCallback(async (): Promise<Optional<AccessLevel>> => {
        const user = await api?.get_user();
        if (user) console.log(`USER: ${user.email} (${user.access_level})`);

        return user ? user.access_level : null
    }, [api]);

    React.useEffect(() => {
        get_access_level().then(access_level => {
            set_has_access(access_level != null && ACCESS_LEVELS.indexOf(access_level) >= ACCESS_LEVELS.indexOf(required_access_level));
        });
    }, [get_access_level]);
    
    if (has_access === null) return (
        <div className="page-loading">
            <div className="page-loading-title">Pirate Pantry</div>
            <Spinner />
        </div>
    );
    return has_access ? <>{children}</> : <Unauthorized />;
}
