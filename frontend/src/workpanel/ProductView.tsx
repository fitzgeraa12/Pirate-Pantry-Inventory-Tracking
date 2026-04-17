import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Product } from "../API";
import { useSearchParams } from "react-router-dom";
import { useLocation } from "react-router-dom";


export default function ProductView({ onEdit }: { onEdit?: (product: Product) => void }): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, set_products] = React.useState<Optional<Array<Product>>>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [search, setSearch] = React.useState("");
    const [inputValue, setInputValue] = React.useState("");
    const [page, setPage] = React.useState(1);
    const [total, setTotal] = React.useState(0);
    const [totalPages, setTotalPages] = React.useState(1);
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;
    const [searchParams] = useSearchParams();
    const searchRef = React.useRef<HTMLInputElement>(null);
    const location = useLocation();
    const refresh = location.state?.refresh;

    React.useEffect(() => {
        const timer = setTimeout(() => { setSearch(inputValue.trim()); setPage(1); }, 300);
        return () => clearTimeout(timer);
    }, [inputValue]);

    React.useEffect(() => {
        const wasFocused = document.activeElement === searchRef.current;
        setIsLoading(true);
        api!.get_products({ search: search || undefined, page, page_size: pageSize }).then((prods) => {
            set_products(prods.data);
            setTotal(prods.total);
            setTotalPages(prods.total_pages);
            setIsLoading(false);
            if (wasFocused) searchRef.current?.focus();
        });
    }, [search, page, refresh]);

    const toolbar = (
        <input
            ref={searchRef}
            className="table-search"
            type="search"
            placeholder="Search products..."
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
        />
    );
    
    return (
        <TableView data={products} toolbar={toolbar} isLoading={isLoading} pageSize={pageSize}
            serverPagination={{ page, total, totalPages, onPageChange: setPage }}
            column_meta={{
            meta: {
                id: { header: "Id" },
                name: { header: "Name" },
                brand: { header: "Brand" },
                quantity: { header: "Quantity" },
                tags: { header: "Tags", cell: (val: Array<string>) => <>{val.join(", ")}</> },
                image_link: { header: "Image" },

                actions: {
                    header: "Actions",
                    cell: (_: any, row: Product) => (
                        <button onClick={ () => onEdit?.(row) 
                        }> Edit </button>
                    ),
                },    
            },
            order: ["id", "actions", "image_link", "name", "brand", "quantity", "tags"],
        }} />
    );
}
