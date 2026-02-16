import { useContext, useMemo, type PropsWithChildren } from 'react';
import { APIContext } from './APIContext';
import { AuthContext } from '../auth/AuthContext';

export interface APIInterface {
    cache_auth: () => Promise<boolean>;
}

function API({ children }: PropsWithChildren) {
    const auth = useContext(AuthContext);
    const api = useMemo<APIInterface>(() => ({
        cache_auth: async (): Promise<boolean> => {
            return false;
        },
    }), [auth]);

    return (
        <APIContext value={api}>
            {children}
        </APIContext>
    );
}

export default API;
