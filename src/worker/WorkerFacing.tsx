import './WorkerFacing.css'
import Titled from '../misc/Titled';
import { useMemo, useState } from 'react';
import { flexRender, getCoreRowModel, getSortedRowModel, useReactTable, type ColumnDef, type SortingState } from '@tanstack/react-table';

interface ProductTableEntry {
    id: number,
    name: string,
    brand?: string | null,
    tags: string[],
    quantity: number,
}

// https://tanstack.com/table/latest/docs/guide/tables
// https://tanstack.com/table/latest/docs/guide/column-defs
// https://stackoverflow.com/questions/76157947/border-radius-doesnt-round-the-borders-of-my-table-but-the-background-color
function WorkerFacing() {
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
                accessorKey: "brand",
                header: "Brand",
            },
            {
                accessorKey: "quantity",
                header: "Quantity",
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

    const db_table = useReactTable({
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
        <Titled title="Workpanel">
            <div id="container">
                <div id="header">
                    <div id="header-top">
                        <div id="title">Pirate Pantry Workpanel</div>
                        <div id="header-top-right">
                            <button id="user-view" className="header-button">User View</button>
                            <button id="log-out" className="header-button">Log Out</button> 
                        </div>
                    </div>
                    <div id="header-bottom">
                        <button id="add-item" className="header-button">Add Item</button>
                        <button id="export-to-xls" className="header-button">Export to XLS</button>
                    </div>
                </div>
                <div id="body">
                    <table id="database-view">
                        <thead>
                            {db_table.getHeaderGroups().map(header_group => {
                                return (
                                <tr key={header_group.id}>
                                    {header_group.headers.map(header => ( // map over the headerGroup headers array
                                    <th key={header.id} colSpan={header.colSpan}>
                                        {flexRender(
                                            header.column.columnDef.header,
                                            header.getContext()
                                        )}
                                    </th>
                                    ))}
                                </tr>
                                )
                            })}
                        </thead>
                        <tbody>
                            {db_table.getRowModel().rows.map(row => (
                                <tr key={row.id}>
                                    {row.getVisibleCells().map(cell => (
                                        <td key={cell.id}>
                                            {flexRender(
                                                cell.column.columnDef.cell,
                                                cell.getContext()
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div id="page-navigation">TODO: Page Navigator</div>
                </div>
                <div id="footer">
                    <div id="quick-statistics">TODO: Statistics</div>
                </div>
            </div>
        </Titled>
    );
}

export default WorkerFacing;
