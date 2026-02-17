import z from 'zod';
import type { PermsSchema } from '../../api/API';
import { useContext, useEffect, useState, type Dispatch, type PropsWithChildren, type SetStateAction } from 'react';
import { PermsContext } from './PermsContext';
import { AuthContext } from '../AuthContext';
import { APIContext } from '../../api/APIContext';

export interface PermsInterface {
    perms: Perms | null,
    set_perms: Dispatch<SetStateAction<Perms | null>>,
}

export type Perms = z.infer<typeof PermsSchema>;

function Perms({ children }: PropsWithChildren) {
    const [perms, set_perms] = useState<Perms | null>(null);

    const auth = useContext(AuthContext);
    const api = useContext(APIContext);

    // Once auth is acquired, acquire perms
    useEffect(() => {
        if (!auth) return;

        api!.get_perms().then((perms) => {
            set_perms(perms);
        }).catch(console.error);
    }, [auth])

    return (
        <PermsContext value={{ perms, set_perms }}>
            {children}
        </PermsContext>
    );
}

export default Perms;
