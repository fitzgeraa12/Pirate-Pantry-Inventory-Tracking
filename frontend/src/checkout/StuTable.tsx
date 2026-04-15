import React from "react";
import type { Optional } from "../misc/misc";
import { useCart } from "../misc/CartContext";
import { Spinner } from "../misc/misc";
import { createColumnHelper, flexRender, getCoreRowModel, getPaginationRowModel, getFilteredRowModel, useReactTable, type ColumnDef, type RowData } from "@tanstack/react-table";
import './StuTable.css'

type BoxedPrimitive<T> = { value: T };
type RowType<T> = T extends object ? T : BoxedPrimitive<T>;

type FieldMeta<T, K extends keyof T> = {
    type?: "field";
    header?: string;
    cell?: (value: T[K], row: T) => React.ReactNode;
};

type ExtraMeta<T extends RowData> = {
    type: "display";
    column: ColumnDef<T, unknown>;
};

type FieldMetaMap<T extends RowData> = {
    [K in keyof T]?: FieldMeta<T, K>;
};

type ExtraMetaMap<T extends RowData, E extends string> = {
    [K in E]: ExtraMeta<T>;
};

type TableMeta<
    T extends RowData,
    E extends string = never,
> = {
    meta: FieldMetaMap<T> & ExtraMetaMap<T, E>;
    order?: Array<keyof T | E>;
};

type AnyMetaEntry<T extends RowData> = FieldMeta<T, keyof T> | ExtraMeta<T>;
function build_cols<T extends RowData>(
    meta: TableMeta<T>["meta"],
    order?: (keyof T | string)[]
): ColumnDef<T, unknown>[] {
    const helper = createColumnHelper<T>();
    const loose = meta as Record<string, AnyMetaEntry<T>>;
    const keys: string[] = order
        ? (order.filter(k => k in loose) as string[])
        : Object.keys(loose);

    return keys.map((key) => {
        const entry = loose[key]!;
        if (entry.type === "display") {
            return entry.column;
        }
        return helper.accessor((row) => row[key as keyof T], {
            id: key,
            header: entry.header ?? key,
            enableGlobalFilter: true,
            ...(entry.cell && {
                cell: (info) => entry.cell!(info.getValue() as T[keyof T], info.row.original),
            }),
        });
    }) as ColumnDef<T, unknown>[];
}

const addRemoveColumns = <T extends RowData>(onAdd: (row: T) => void, onRemove: (row: T) => void): ColumnDef<T, unknown>[] => [
    {
        id: "__add__",
        header: "Add",
        cell: ({ row }) => (
            <button className="row-action-button" onClick={() => onAdd(row.original)}>
                +
            </button>
        ),
    },
    {
        id: "__remove__",
        header: "Remove",
        cell: ({ row }) => (
            <button className="row-action-button" onClick={() => onRemove(row.original)}>
                -
            </button>
        ),
    },
];

export default function TableView<
    T,
    E extends string = never,
    M extends FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E>
        = FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E>
>({ data, column_meta, toolbar, isLoading, pageSize = 20, serverPagination, searchTerm }: {
    data: Optional<Array<T>>;
    column_meta: {
        meta: M;
        order?: Array<keyof M>;
    };
    toolbar?: React.ReactNode;
    isLoading?: boolean;
    pageSize?: number;
    serverPagination?: { page: number; total: number; totalPages: number; onPageChange: (page: number) => void };
    searchTerm?: string,
}): React.ReactNode {
    const { addItem, removeItem } = useCart();

    const dataColumns = React.useMemo(
        () => build_cols(column_meta.meta as TableMeta<T>["meta"], column_meta.order as string[]),
        [column_meta]
    );

    const columns = React.useMemo(
        () => [...dataColumns, ...addRemoveColumns<T>((row) => addItem(row), (row) => removeItem((row as any).id))],
        [dataColumns, addItem, removeItem]
    );

    const table = useReactTable({
        data: data ?? [],
        columns,
        state:{ globalFilter: searchTerm,},
        onGlobalFilterChange: () => {},
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        globalFilterFn: (row, _, filterValue) => {
            const search = String(filterValue).toLowerCase();

            return Object.values(row.original).some(val =>
                String(val).toLowerCase().includes(search)
            );
        },
        initialState: { pagination: { pageSize } },
        manualPagination: serverPagination !== undefined,
        ...(serverPagination !== undefined && { pageCount: serverPagination.totalPages }),
    });

    const { pageIndex, pageSize: currentPageSize } = table.getState().pagination;
    const total = serverPagination?.total ?? (data ?? []).length;
    const currentPage = serverPagination !== undefined ? serverPagination.page : pageIndex + 1;
    const from = total === 0 ? 0 : (currentPage - 1) * currentPageSize + 1;
    const to = Math.min(currentPage * currentPageSize, total);

    return (data !== null || toolbar) ? (
        <div className="table-view-outer">
        <div className="table-view-wrapper">
            {isLoading || data === null ? (
                <div className="table-loading"><Spinner /></div>
            ) : (<table className="table-view">
                <thead className="table-view-header">
                    {table.getHeaderGroups().map(headerGroup => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map(header => (
                                <th
                                    className="table-view-header-cell"
                                    key={header.id}
                                >
                                    {flexRender(header.column.columnDef.header, header.getContext())}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody className="table-view-body">
                    {table.getRowModel().rows.map(row => (
                        <tr
                            key={row.id}
                        >
                            {row.getVisibleCells().map(cell => (
                                <td className="table-view-data-cell" key={cell.id}>
                                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>)}
        </div>
        <div className="table-view-pagination">
            <span style={{ flex: 1 }} />
            <button
                className="pagination-button"
                onClick={() => serverPagination ? serverPagination.onPageChange(serverPagination.page - 1) : table.previousPage()}
                disabled={serverPagination ? serverPagination.page <= 1 : !table.getCanPreviousPage()}
            >&#8592; Prev</button>
            <span className="pagination-info">{from}–{to} of {total}</span>
            <button
                className="pagination-button"
                onClick={() => serverPagination ? serverPagination.onPageChange(serverPagination.page + 1) : table.nextPage()}
                disabled={serverPagination ? serverPagination.page >= serverPagination.totalPages : !table.getCanNextPage()}
            >Next &#8594;</button>
        </div>
        </div>
    ) : (
        <div className="table-view-outer">
            <div className="table-loading">
                <Spinner />
            </div>
        </div>
    );
}
