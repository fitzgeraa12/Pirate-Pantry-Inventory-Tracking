
import { useMemo, useState, useEffect } from "react";
import View from "../worker/views/View";
import { getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";
import { useCart } from "../misc/CartContext";
interface ProductTableEntry {
    id: number,
    name: string,
    brand?: string | null,
    tags: string[],
    quantity: number,
}

interface ProductViewProps {
    searchTerm?: string;
}

function PantryView({ searchTerm: externalSearchTerm }: ProductViewProps = {}) {
    const { addToCart, removeFromCart} = useCart(); 
    const columns = useMemo<ColumnDef<ProductTableEntry>[]>(() => {
        return [
            {
                accessorKey: "id",
                header: "ID",
            },
            {
                accessorKey: "name",
                header: "Name",
            },
            {
                accessorKey: "quantity",
                header: "Quantity",
            },
            {
                accessorKey: "brand",
                header: "Brand",
            },
            {
                accessorKey: "tags",
                header: "Tags",
            },
            {
                id: "actions",
                cell: ({row}) => (
                    <>
                        <button className="table-entry-button"
                        onClick={()=> addToCart(String(row.original.id), row.original.name, row.original.quantity)}>Add</button>
                        <button className="table-entry-button"
                        onClick={()=>removeFromCart(String(row.original.id))}>Remove</button>
                    </>
                ),
            },
        ]
    }, []);

    const [sorting, set_sorting] = useState<SortingState>([
        { id: "id", desc: false }
    ])

    const [internalSearch, setInternalSearch] = useState("");
    const search = externalSearchTerm !== undefined ? externalSearchTerm : internalSearch;

    const[products, setProducts] = useState<ProductTableEntry[]>([]);

    useEffect(() =>{
        const timeout = setTimeout( async () => {
            //const response = await fetch(`/api/products?search=${encodeURIComponent(search)}`);//api
            const response = await fetch(`http://localhost:3001/api/products?search=${encodeURIComponent(search)}`);
            const data = await response.json();
            setProducts(data);
        }, 300);

        return() => clearTimeout(timeout);
    }, [search]);

    useEffect(() => {
    const timeout = setTimeout(async () => {

        // pretend this came from the database
        const mockDatabase = [
            { id: 1, name: "Milk", brand: "Horizon", tags: ["dairy"], quantity: 12 },
            { id: 2, name: "Bread", brand: "Wonder", tags: ["grain"], quantity: 7 },
            { id: 3, name: "Peanut Butter", brand: "Jif", tags: ["protein"], quantity: 5 },
            { id: 4, name: "Cereal", brand: "General Mills", tags: ["breakfast"], quantity: 10 },
        ];

        const lower = search.toLowerCase();

        const results = mockDatabase.filter(p =>
            p.name.toLowerCase().includes(lower) ||
            p.brand?.toLowerCase().includes(lower) ||
            p.tags.some(tag => tag.toLowerCase().includes(lower))
        );

        setProducts(results);

    }, 300);

    return () => clearTimeout(timeout);
}, [search]);

    const tbl = useReactTable({
        data: products, 
        columns,
        getCoreRowModel: getCoreRowModel(),
        getSortedRowModel: getSortedRowModel(),
        state: {
            sorting,
        },
        onSortingChange: set_sorting,
    })

    return (
        <View id="view" tbl={tbl} header_children={
            externalSearchTerm === undefined ? (
                <input  
                    type="text"
                    placeholder="Search products..."
                    value={internalSearch}
                    onChange={(e) => setInternalSearch(e.target.value)}
                />
            ) : null
        } />
    );
}

export default PantryView;
