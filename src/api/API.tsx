import { useCallback, useContext, useMemo, type PropsWithChildren } from 'react';
import { APIContext } from './APIContext';
import { AuthContext } from '../auth/AuthContext';
import axios, { type AxiosResponse } from 'axios';
import z from 'zod';
import { unreachable } from '../misc/misc';

// https://zod.dev/basics
const CacheAuthResponse = z.object({
  success: z.boolean(),
});

// https://zod.dev/basics?id=inferring-types
const PermsSchema = z.enum(["User", "Trusted", "Admin"]);
export type Perms = z.infer<typeof PermsSchema>;
const GetPermsResponse = z.object({
    perms: PermsSchema,
});

export interface APIInterface {
    cache_auth: () => Promise<boolean>,
    get_perms: () => Promise<Perms>,
}

class NoAuthError extends Error {
  constructor() {
    super("No authentication");
    this.name = "NoAuthError";
}
}

const API_URL = "https://api.piratepantry.com";
type HttpMethod = "GET" | "POST";

function API({ children }: PropsWithChildren) {
    const auth = useContext(AuthContext);

    /**
     * @throws NoAuthError
     */
    const get_auth = useCallback((): string => {
        if (!auth) throw new NoAuthError();

        return auth;
    }, [auth]);

    const api = useMemo<APIInterface>(() => {
        /**
         * @returns string
         */
        const prepend_api_url = (partial_endpoint: string): string => {
            return `${API_URL}/${partial_endpoint}`;
        };

        /**
         * https://www.npmjs.com/package/axios
         * 
         * @returns boolean
         */
        const api_call = async (method: HttpMethod, partial_endpoint: string): Promise<AxiosResponse> => {
            const endpoint = prepend_api_url(partial_endpoint);
            
            switch (method) {
                case "GET":
                    return axios.get(endpoint);
                case "POST":
                    return axios.post(endpoint);
                default:
                    unreachable("Unrecognized HTTP method");
            }
        };

        return {
            /**
             * @throws NoAuthError, AxiosError, ZodError
             * @returns boolean
             */
            cache_auth: async (): Promise<boolean> => {
                return true; // FIXME: temporary until API is set up

                const response = await api_call("GET", `cache_auth?auth=${get_auth()}`);
                const parsed = await CacheAuthResponse.parseAsync(response.data);
                
                return parsed.success;
            },

            /**
             * @throws NoAuthError, AxiosError, ZodError
             * @returns Perms
             */
            get_perms: async (): Promise<Perms> => {
                return "Admin"; // FIXME: temporary until API is set up

                const response = await api_call("GET", `get_perms?auth=${get_auth()}`);
                const parsed = await GetPermsResponse.parseAsync(response.data);
                
                return parsed.perms;
            },
        }
    }, [auth]);

    return (
        <APIContext value={api}>
            {children}
        </APIContext>
    );
}

export default API;
