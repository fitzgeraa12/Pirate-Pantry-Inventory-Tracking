
import React from "react";
import axios from "axios";
import z from "zod";
import type { Optional } from "./misc/misc";

const API_PORT = import.meta.env.VITE_API_PORT
const API_URL = API_PORT ? `${import.meta.env.VITE_API_URL}:${API_PORT}` : import.meta.env.VITE_API_URL


export const api_base = axios.create({
    baseURL: API_URL,
});

api_base.interceptors.request.use((config) => {
    const session = localStorage.getItem('session');
    if (session) config.headers.Authorization = session;
    return config;
});

const AccessLevelSchema = z.enum(["trusted", "admin"]);
export type AccessLevel = z.infer<typeof AccessLevelSchema>

const UserSchema = z.object({
    id: z.string(),
    email: z.string(),
    access_level: AccessLevelSchema,
})
export type User = z.infer<typeof UserSchema>

const WhoAmISchema = z.object({
    id: z.string().optional().nullable(),
})
type WhoAmI = z.infer<typeof WhoAmISchema>

const BrandSchema = z.object({
    name: z.string(),
})
export type Brand = z.infer<typeof BrandSchema>

const TagSchema = z.object({
    label: z.string(),
})
export type Tag = z.infer<typeof TagSchema>

const ProductSchema = z.object({
    id: z.number(),
    name: z.string(),
    brand: z.string().nullable().optional(),
    quantity: z.number(),
    image_link: z.string().nullable().optional(),
    tags: z.array(z.string()),
})
export type Product = z.infer<typeof ProductSchema>

function PaginatedRequestSchema<T extends z.ZodTypeAny>(item_schema: T) {
    return z.union([z.object({
        page: z.number(),
        page_size: z.number(),
    }), item_schema]);
}

type PaginatedRequest<T> = T & {
    page?: Optional<number>,
    page_size?: Optional<number>,
};

function PaginatedResponseSchema<T extends z.ZodType>(item_schema: T) {
    return z.object({
        data: z.array(item_schema),
        total: z.number(),
        total_pages: z.number(),
    });
}

type PaginatedResponse<T> = {
    data: Array<T>;
    total: number;
    total_pages: number;
};

const SessionSchema = z.object({
    id: z.string(),
    user_email: z.string().nullable().optional(),
    created_at: z.number(),
    expires_at: z.number(),
    is_current: z.boolean(),
})
export type Session = z.infer<typeof SessionSchema>

export namespace API {
    export type Type = {
        get_user: () => Promise<Optional<User>>,
        get_users: () => Promise<Array<User>>,
        whoami: () => Promise<Optional<string>>,
        get_products: (args?: PaginatedRequest<GetProductsArgs>) => Promise<PaginatedResponse<Product>>,
        get_brands: (args?: PaginatedRequest<GetBrandsArgs>) => Promise<PaginatedResponse<Brand>>,
        get_tags: (args?: PaginatedRequest<GetTagsArgs>) => Promise<PaginatedResponse<Tag>>,
        get_settings: () => Promise<Record<string, string>>,
        update_settings: (patch: Record<string, string | number>) => Promise<Record<string, string>>,
        add_user: (email: string, access_level: AccessLevel) => Promise<User>,
        update_user: (id: string, patch: { access_level: AccessLevel }) => Promise<User>,
        get_sessions: () => Promise<Array<Session>>,
        revoke_session: (id: string) => Promise<void>,
    }

    interface GetProductsArgs {
        id?: Optional<number>,
        name?: Optional<string>,
        brand?: Optional<string>,
        quantity?: Optional<string>,
        image_link?: Optional<string>,
        tags?: Optional<Array<string>>,
    }

    interface GetBrandsArgs {
        name?: Optional<string>,
    }

    interface GetTagsArgs {
        label?: Optional<string>,
    }

    export const Context = React.createContext<Optional<Type>>(null);
    
    export function Component({ children }: React.PropsWithChildren): React.ReactNode {
        const api = React.useMemo<Type>(() => {
            
            const api_get = async<T extends object, U extends z.ZodType>(url: string, schema: U, params?: T): Promise<any> => {
                return schema.parse(
                    (await api_base.get(url, params ? {params} : undefined)).data
                );
            }

            return {
                get_user: async (): Promise<Optional<User>> => {
                    return await api_get("/user", UserSchema.optional().nullable());
                },

                get_users: async (): Promise<Array<User>> => {
                    return await api_get("/users", z.array(UserSchema));
                },

                whoami: async (): Promise<Optional<string>> => {
                    return (await api_get("/auth/whoami", WhoAmISchema)).id
                },

                get_products: async(args?: PaginatedRequest<GetProductsArgs>): Promise<PaginatedResponse<Product>> => {
                    return await api_get("products", PaginatedResponseSchema(ProductSchema), args);
                },

                get_brands: async(args?: PaginatedRequest<GetBrandsArgs>): Promise<PaginatedResponse<Brand>> => {
                    return await api_get("brands", PaginatedResponseSchema(BrandSchema), args);
                },

                get_tags: async(args?: PaginatedRequest<GetTagsArgs>): Promise<PaginatedResponse<Tag>> => {
                    return await api_get("tags", PaginatedResponseSchema(TagSchema), args);
                },

                get_settings: async (): Promise<Record<string, string>> => {
                    return (await api_base.get("/settings")).data as Record<string, string>;
                },

                update_settings: async (patch: Record<string, string | number>): Promise<Record<string, string>> => {
                    return (await api_base.patch("/settings", patch)).data;
                },

                add_user: async (email: string, access_level: AccessLevel): Promise<User> => {
                    return (await api_base.post("/user", null, { params: { email, access_level } })).data;
                },

                update_user: async (id: string, patch: { access_level: AccessLevel }): Promise<User> => {
                    return (await api_base.patch(`/user/${id}`, patch)).data;
                },

                get_sessions: async (): Promise<Array<Session>> => {
                    return await api_get("/sessions", z.array(SessionSchema));
                },

                revoke_session: async (id: string): Promise<void> => {
                    await api_base.delete(`/session/${id}`);
                },
            }
        }, []);

        return (
            <Context value={api}>
                {children}
            </Context>
        );
    }
}
