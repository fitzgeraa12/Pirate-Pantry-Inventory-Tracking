
import { useMemo, useState, useEffect } from "react";
import View from "./View";
import { getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";
import { useCart } from "../../misc/CartContext";
interface ProductTableEntry {
    id: number,
    name: string,
    brand?: string | null,
    tags: string[],
    quantity: number,
}

function ProductView() {
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
                        onClick={()=> addToCart(row.original.id)}>Add</button>
                        <button className="table-entry-button"
                        onClick={()=>removeFromCart(row.original.id)}>Remove</button>
                    </>
                ),
            },
        ]
    }, []);

    // const [product_table_entries, _set_product_table_entries] = useState<Array<ProductTableEntry>>([
    //     {
    //         id: 2,
    //         name: "TEST2",
    //         brand: null,
    //         tags: [],
    //         quantity: 1,
    //     },
    //     {
    //         id: 1,
    //         name: "TEST",
    //         brand: null,
    //         tags: [],
    //         quantity: 7,
    //     },
    //     {
    //         id: 3,
    //         name: "TEST3",
    //         brand: "General Mills",
    //         tags: [],
    //         quantity: 3,
    //     },
    //     {
    //         id: 4,
    //         name: "TEST4",
    //         brand: "General Mills",
    //         tags: [],
    //         quantity: ,
    //     },        
    //     {
    //         id: 5,
    //         name: "TEST5",
    //         brand: "HEB",
    //         tags: [],
    //         quantity: 4,
    //     },
    //     {
    //         id: 6,
    //         name: "TEST6",
    //         brand: "HEB",
    //         tags: ["PROTIEN"],
    //         quantity: 6,
    //     },
    // ]);
    const [sorting, set_sorting] = useState<SortingState>([
        { id: "id", desc: false }
    ])

    const [search, setSearch] = useState("");

    const[products, setProducts] = useState<ProductTableEntry[]>([]);

    // useEffect(() =>{
    //     const timeout = setTimeout( async () => {
    //         //const response = await fetch(`/api/products?search=${encodeURIComponent(search)}`);//api
    //         const response = await fetch(`http://localhost:3001/api/products?search=${encodeURIComponent(search)}`);
    //         const data = await response.json();
    //         setProducts(data);
    //     }, 300);

    //     return() => clearTimeout(timeout);
    // }, [search]);

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
            <>
                <input  
                    type="text"
                    placeholder="Search products..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </>
        } />
    );
}

export default ProductView;
