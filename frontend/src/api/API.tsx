import { useCallback, useContext, useMemo, type PropsWithChildren } from 'react';
import { APIContext } from './APIContext';
import { AuthContext } from '../auth/AuthContext';
import axios, { type AxiosResponse } from 'axios';
import z from 'zod';
import type { Perms } from '../auth/perms/Perms';
// import { unreachable } from '../misc/misc';

// // Cache auth
// // https://zod.dev/basics
// const CacheAuthResponse = z.object({
//   success: z.boolean(),
// });

// Perms
// https://zod.dev/basics?id=inferring-types
export const PermsSchema = z.enum(["User", "Trusted", "Admin"]);
export const GetPermsResponse = z.object({
    perms: PermsSchema,
});

// Product
export const ProductSchema = z.object({
    id: z.number(),
    name: z.string(),
    brand: z.string(),
    quantity: z.number(),
    image_link: z.nullable(z.string()),
    tags: z.array(z.string()).default([]),
});
export type Product = z.infer<typeof ProductSchema>;
export const ProductResponse = z.object({
    product: z.optional(ProductSchema),
});

export const ProductsArrayResponse = z.object({
    products: z.array(ProductSchema),
});

// Brand
export const BrandSchema = z.object({
    name: z.string(),
    id: z.number(),
});
export type Brand = z.infer<typeof BrandSchema>;
export const BrandResponse = z.object({
    brand: z.optional(BrandSchema),
});

export const AllBrandsResponse = z.object({
    brands: z.array(BrandSchema),
});

// Tag
export const TagSchema = z.object({
    name: z.string(),
    id: z.number(),
});
export type Tag = z.infer<typeof TagSchema>;
export const TagResponse = z.object({
    tag: z.optional(TagSchema),
});

export const AllTagsResponse = z.object({
    tags: z.array(TagSchema),
});

export interface APIInterface {
    inventory: () => Promise<Array<Product>>,
    cache_auth: () => Promise<boolean>,
    perms: () => Promise<Perms>,
}

class NoAuthError extends Error {
  constructor() {
    super("No authentication");
    this.name = "NoAuthError";
  }
}

const API_URL = "https://fitzgeraa12.pythonanywhere.com";
// type HttpMethod = "GET" | "POST";

function API({ children }: PropsWithChildren) {
    const auth = useContext(AuthContext);

    /**
     * @throws NoAuthError
     */
    const get_auth = useCallback((): string => {
        if (!auth) throw new NoAuthError();

        return auth.token;
    }, [auth]);

    const api = useMemo<APIInterface>(() => {
        // /**
        //  * @returns string
        //  */
        // const prepend_api_url = (partial_endpoint: string, params: URLSearchParams): string => {
        //     return `${API_URL}/${partial_endpoint}?${params.toString()}`;
        // };

        // /**
        //  * @returns URLSearchParams
        //  */
        // const auth_url_search_params = (): URLSearchParams => {
        //     return new URLSearchParams({ auth: get_auth() });
        // };

        // /**
        //  * https://www.npmjs.com/package/axios
        //  */
        // const api_call = async (method: HttpMethod, partial_endpoint: string, params: URLSearchParams): Promise<AxiosResponse> => {
        //     const endpoint = prepend_api_url(partial_endpoint, params);
            
        //     switch (method) {
        //         case "GET":
        //             return axios.get(endpoint);
        //         case "POST":
        //             return axios.post(endpoint);
        //         default:
        //             unreachable("Unrecognized HTTP method");
        //     }
        // };

        /**
         * Makes an authenticated GET request to the Flask API
         */
        const authenticated_get = async (endpoint: string): Promise<AxiosResponse> => {
            return axios.get(`${API_URL}${endpoint}`, {
                headers: {
                    Authorization: `Bearer ${get_auth()}`,
                },
            });
        };

        return {
            /**
             * @throws NoAuthError, AxiosError, ZodError
             * @returns Array<Product>
             */
            inventory: async (): Promise<Array<Product>> => {
                const response = await authenticated_get('/api/inventory');
                return z.array(ProductSchema).parseAsync(response.data);
            },

            cache_auth: async (): Promise<boolean> => {
                return true;
            },

            perms: async (): Promise<Perms> => {
                return 'Admin'; // FIXME: Dev only
            },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns boolean
        //      */
        //     cache_auth: async (): Promise<boolean> => {
        //         const params = auth_url_search_params();

        //         const response = await api_call("GET", "cache_auth", params);
        //         const parsed = await CacheAuthResponse.parseAsync(response.data);
                
        //         return parsed.success;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Perms
        //      */
        //     perms: async (): Promise<Perms> => {
        //         return "Admin";

        //         const params = auth_url_search_params();

        //         const response = await api_call("GET", "perms", params);
        //         const parsed = await GetPermsResponse.parseAsync(response.data);
                
        //         return parsed.perms;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Product | undefined
        //      */
        //     product: async (id: number): Promise<Product | undefined> => {
        //         const params = auth_url_search_params();
        //         params.append("id", id.toString());

        //         const response = await api_call("GET", "product", params);
        //         const parsed = await ProductResponse.parseAsync(response.data);
                
        //         return parsed.product;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Array<Product>
        //      */
        //     query_products: async (name?: string, brand?: string, tags?: Array<string>): Promise<Array<Product>> => {
        //         const params = auth_url_search_params();
        //         if (name) params.append("name", name);
        //         if (brand) params.append("brand", brand);
        //         if (tags) params.append("tags", tags.join(","));

        //         const response = await api_call("GET", "query_products", params);
        //         const parsed = await ProductsArrayResponse.parseAsync(response.data);
                
        //         return parsed.products;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Array<Product>
        //      */
        //     all_products: async (): Promise<Array<Product>> => {
        //         const params = auth_url_search_params();

        //         const response = await api_call("GET", "all_products", params);
        //         const parsed = await ProductsArrayResponse.parseAsync(response.data);
                
        //         return parsed.products;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Brand | undefined
        //      */
        //     brand: async (id: number): Promise<Brand | undefined> => {
        //         const params = auth_url_search_params();
        //         params.append("id", id.toString());

        //         const response = await api_call("GET", "brand", params);
        //         const parsed = await BrandResponse.parseAsync(response.data);
                
        //         return parsed.brand;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Array<Brand>
        //      */
        //     all_brands: async (): Promise<Array<Brand>> => {
        //         const params = auth_url_search_params();

        //         const response = await api_call("GET", "all_brands", params);
        //         const parsed = await AllBrandsResponse.parseAsync(response.data);
                
        //         return parsed.brands;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Tag | undefined
        //      */
        //     tag: async (id: number): Promise<Tag | undefined> => {
        //         const params = auth_url_search_params();
        //         params.append("id", id.toString());

        //         const response = await api_call("GET", "tag", params);
        //         const parsed = await TagResponse.parseAsync(response.data);
                
        //         return parsed.tag;
        //     },

        //     /**
        //      * @throws NoAuthError, AxiosError, ZodError
        //      * @returns Array<Tag>
        //      */
        //     all_tags: async (): Promise<Array<Tag>> => {
        //         const params = auth_url_search_params();

        //         const response = await api_call("GET", "all_tags", params);
        //         const parsed = await AllTagsResponse.parseAsync(response.data);
                
        //         return parsed.tags;
        //     },
        }
    }, [auth]);

    return (
        <APIContext value={api}>
            {children}
        </APIContext>
    );
}

export default API;