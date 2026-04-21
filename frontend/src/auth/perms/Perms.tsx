import { useContext, useEffect, useState, type Dispatch, type PropsWithChildren, type SetStateAction } from 'react';
import { PermsContext } from './PermsContext';
import { AuthContext } from '../AuthContext';
import { APIContext } from '../../api/APIContext';
import type { Perms } from '../../api/API';
import type { Optional } from '../../misc/misc';

export interface PermsInterface {
    perms: Perms,
    set_perms: Dispatch<SetStateAction<Perms>>,
}

function PermsProvider({ children }: PropsWithChildren) {
    const [perms, set_perms] = useState<Perms>("user");

    const auth = useContext(AuthContext);
    const api = useContext(APIContext);

    // Once auth is acquired, acquire perms
    useEffect(() => {
        if (auth.is_none()) return;

        api.unwrap().perms().then((perms) => {
            set_perms(perms);
        }).catch(console.error);
    }, [auth])

    return (
        <PermsContext value={Option.some({ perms: perms, set_perms })}>
            {children}
        </PermsContext>
    );
}

export default PermsProvider;
