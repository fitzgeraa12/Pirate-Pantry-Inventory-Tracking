import { useMemo, useState } from "react";
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

    const [product_table_entries, set_product_table_entries] = useState<Array<ProductTableEntry>>([
        {
            id: 2,
            name: "TEST2",
            brand: null,
            tags: [],
            quantity: 1,
        },
        {
            id: 1,
            name: "TEST",
            brand: null,
            tags: [],
            quantity: 7,
        },
        {
            id: 3,
            name: "TEST3",
            brand: "General Mills",
            tags: [],
            quantity: 3,
        },
    ]);
    const [sorting, set_sorting] = useState<SortingState>([
        { id: "id", desc: false }
    ])

    const tbl = useReactTable({
        data: product_table_entries, 
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
            </>
        } />
    );
}

export default ProductView;
