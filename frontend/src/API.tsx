
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
    brand: BrandSchema.nullable().optional(),
    quantity: z.number(),
    image_link: z.string().nullable().optional(),
    tags: z.array(TagSchema),
})
export type Product = z.infer<typeof ProductSchema>

function PaginatedSchema<T extends z.ZodTypeAny>(item_schema: T) {
    return z.object({
        data: z.array(item_schema),
        total: z.number(),
        total_pages: z.number(),
    });
}

type Paginated<T> = {
    data: Array<T>;
    total: number;
    total_pages: number;
};

export namespace API {
    export type Type = {
        get_user: () => Promise<Optional<User>>,
        whoami: () => Promise<Optional<string>>,
        products:() => Promise<Paginated<Product>>,
        brands: () => Promise<Paginated<Brand>>,
        tags: () => Promise<Paginated<Tag>>,
    }

    export const Context = React.createContext<Optional<Type>>(null);
    
    export function Component({ children }: React.PropsWithChildren): React.ReactNode {
        const api = React.useMemo<Type>(() => {
            return {
                get_user: async (): Promise<Optional<User>> => {
                    try {
                        const response = await api_base.get("/user");
                        if (response.data === null) return null;
                        return UserSchema.parse(response.data);
                    } catch {
                        return null;
                    }
                },

                whoami: async (): Promise<Optional<string>> => {
                    try {
                        const response = await api_base.get("/auth/whoami");
                        return response.data.id ?? null;
                    } catch {
                        return null;
                    }
                },

                products: async(): Promise<Paginated<Product>> => {
                    const response = await api_base.get("products");
                    return PaginatedSchema(ProductSchema).parse(response.data);
                },

                brands: async(): Promise<Paginated<Brand>> => {
                    const response = await api_base.get("brands");
                    return PaginatedSchema(BrandSchema).parse(response.data);
                },

                tags: async(): Promise<Paginated<Tag>> => {
                    const response = await api_base.get("tags");
                    return PaginatedSchema(TagSchema).parse(response.data);
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
