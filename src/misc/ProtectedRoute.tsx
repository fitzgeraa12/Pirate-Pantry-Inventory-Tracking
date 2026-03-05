import { useCallback, useContext, type PropsWithChildren } from "react";
import { PermsContext } from "../auth/perms/PermsContext";
import Unauthorized from "./Unauthorized";
import type { Perms } from "../auth/perms/Perms";

interface ProtectedRouteProps {
    required_perms: Perms[],
}

function ProtectedRoute({ required_perms, children }: PropsWithChildren<ProtectedRouteProps>) {
    const { perms } = useContext(PermsContext)!;
    
    const has_perms = useCallback((): boolean => {
        return perms ? required_perms.includes(perms) : false;
    }, [perms])
    
    return has_perms() ? (
        <>{children}</>
    ) : (
        <Unauthorized />
    );
}

export default ProtectedRoute;
