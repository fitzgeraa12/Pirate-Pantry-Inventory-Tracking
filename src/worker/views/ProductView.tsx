import { useMemo, useState } from "react";
import View from "./View";
import { getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from "@tanstack/react-table";

interface ProductTableEntry {
    id: number,
    name: string,
    brand?: string | null,
    tags: string[],
    quantity: number,
}

function ProductView() {
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
                cell: (_cell_ctx) => (
                    <>
                        <button className="table-entry-button">Edit</button>
                        <button className="table-entry-button">Delete</button>
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
                <button id="add-item" className="body-header-button">Add Item</button>
                <button id="export-to-xls" className="body-header-button">Export to XLS</button>
            </>
        } />
    );
}

export default ProductView;
