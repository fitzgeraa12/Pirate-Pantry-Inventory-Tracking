
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
    access_level: AccessLevelSchema
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

export namespace API {
    export type Type = {
        get_user: () => Promise<Optional<User>>,
        whoami: () => Promise<Optional<string>>,
        get_products:(args?: PaginatedRequest<GetProductsArgs>) => Promise<PaginatedResponse<Product>>,
        get_brands: (args?: PaginatedRequest<GetBrandsArgs>) => Promise<PaginatedResponse<Brand>>,
        get_tags: (args?: PaginatedRequest<GetTagsArgs>) => Promise<PaginatedResponse<Tag>>,
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
                }
            }
        }, []);

        return (
            <Context value={api}>
                {children}
            </Context>
        );
    }
}
