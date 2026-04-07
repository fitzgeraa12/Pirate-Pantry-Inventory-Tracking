import React from "react";
import StuTable from "./StuTable";
import { createColumnHelper } from "@tanstack/react-table";
import type { Optional } from "../misc/misc";
import { API, type Product } from "../API";
import { useCart } from "../misc/CartContext";

export default function PantryView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, set_products] = React.useState<Optional<Array<Product>>>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [search, setSearch] = React.useState("");
    const [inputValue, setInputValue] = React.useState("");
    const [page, setPage] = React.useState(1);
    const [total, setTotal] = React.useState(0);
    const [totalPages, setTotalPages] = React.useState(1);
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;
    const columnHelper = createColumnHelper<Product>();
    const { addToCart, removeFromCart} = useCart();

    const searchRef = React.useRef<HTMLInputElement>(null);

    const actionColumn = React.useMemo(() => ({
        type: "display",
        column: columnHelper.display({
            id: "actions",
            header: "Actions",
            size: 150,
            cell: ({row}) => {
                const { id, name, quantity } = row.original;
                        
                return (
                    <div style= {{ display: "flex", gap: "0.5rem" }}>
                        <button 
                            className="table-entry-button"
                            onClick={(e) => {
                                e.stopPropagation();
                                addToCart(id, name, quantity);
                            }}
                        >
                        Add
                        </button>

                    <button
                            className="table-entry-button"
                            onClick={(e) => {
                                e.stopPropagation();
                                removeFromCart(id);
                            }}
                        >
                            Remove
                        </button>
                    </div>
                );
            }
        })
    }), [addToCart, removeFromCart, columnHelper]);

    React.useEffect(() => {
        const timer = setTimeout(() => { setSearch(inputValue.trim()); setPage(1); }, 300);
        return () => clearTimeout(timer);
    }, [inputValue]);

    React.useEffect(() => {
        const wasFocused = document.activeElement === searchRef.current;
        setIsLoading(true);
        api!.get_products({ name: search ? `%${search}%` : undefined, page, page_size: pageSize }).then((prods) => {
            set_products(prods.data);
            setTotal(prods.total);
            setTotalPages(prods.total_pages);
            setIsLoading(false);
            if (wasFocused) searchRef.current?.focus();
        });
    }, [search, page, api, pageSize]);

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
        <StuTable data={products} toolbar={toolbar} isLoading={isLoading} pageSize={pageSize}
            serverPagination={{ page, total, totalPages, onPageChange: setPage }}
            column_meta={{
            meta: {
                id: { header: "Id" },
                name: { header: "Name" },
                brand: { header: "Brand" },
                quantity: { header: "Quantity" },
                tags: { header: "Tags", cell: (val: Array<string>) => <>{val.join(", ")}</> },
                image_link: { header: "Image" },

                actions: actionColumn,
            },
            order: ["id", "actions", "image_link", "name", "brand", "quantity", "tags"],
        }}
     />
);
}
