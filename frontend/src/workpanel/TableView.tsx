import React from "react";
import type { Optional } from "../misc/misc";
import { Spinner } from "../misc/misc";
import { createColumnHelper, flexRender, getCoreRowModel, getPaginationRowModel, getFilteredRowModel, useReactTable, type ColumnDef, type RowData, type RowSelectionState } from "@tanstack/react-table";
import './TableView.css'

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

type TableAction<T> = {
    label: string;
    onClick: (rows: T[]) => void;
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
            ...(entry.cell && {
                cell: (info) => entry.cell!(info.getValue() as T[keyof T], info.row.original),
            }),
        });
    }) as ColumnDef<T, unknown>[];
}

const checkboxColumn = <T extends RowData>(): ColumnDef<T, unknown> => ({
    id: "__select__",
    size: 40,
    header: ({ table }) => (
        <input
            type="checkbox"
            className="row-checkbox"
            checked={table.getIsAllPageRowsSelected()}
            ref={el => { if (el) el.indeterminate = table.getIsSomePageRowsSelected(); }}
            onChange={table.getToggleAllPageRowsSelectedHandler()}
        />
    ),
    cell: ({ row }) => (
        <input
            type="checkbox"
            className="row-checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            onClick={e => e.stopPropagation()}
        />
    ),
});

export default function TableView<
    T,
    E extends string = never,
    M extends FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E>
        = FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E>
>({ data, column_meta, actions, toolbar, isLoading, pageSize = 20, serverPagination }: {
    data: Optional<Array<T>>;
    column_meta: {
        meta: M;
        order?: Array<keyof M>;
    };
    actions?: TableAction<T>[];
    toolbar?: React.ReactNode;
    isLoading?: boolean;
    pageSize?: number;
    serverPagination?: { page: number; total: number; totalPages: number; onPageChange: (page: number) => void };
}): React.ReactNode {
    const [rowSelection, setRowSelection] = React.useState<RowSelectionState>({});
    const [editMode, setEditMode] = React.useState(false);

    const dataColumns = React.useMemo(
        () => build_cols(column_meta.meta as TableMeta<T>["meta"], column_meta.order as string[]),
        [column_meta]
    );

    const columns = React.useMemo(
        () => (actions && editMode) ? [checkboxColumn<RowType<T>>() as ColumnDef<T, unknown>, ...dataColumns] : dataColumns,
        [dataColumns, actions, editMode]
    );

    const table = useReactTable({
        data: data ?? [],
        columns,
        state: { rowSelection },
        onRowSelectionChange: setRowSelection,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        initialState: { pagination: { pageSize } },
        manualPagination: serverPagination !== undefined,
        pageCount: serverPagination?.totalPages ?? -1,
    });

    const { pageIndex, pageSize: currentPageSize } = table.getState().pagination;
    const total = serverPagination?.total ?? (data ?? []).length;
    const currentPage = serverPagination !== undefined ? serverPagination.page : pageIndex + 1;
    const from = total === 0 ? 0 : (currentPage - 1) * currentPageSize + 1;
    const to = Math.min(currentPage * currentPageSize, total);

    const selectedRows = table.getSelectedRowModel().rows.map(r => r.original);
    const selectedCount = selectedRows.length;

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
                                    style={header.column.id === "__select__" ? { width: 40 } : undefined}
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
                            className={row.getIsSelected() ? "row-selected" : ""}
                            onClick={() => editMode && row.toggleSelected()}
                            style={{ cursor: (actions && editMode) ? "pointer" : undefined }}
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
            {toolbar && <>{toolbar}<span className="pagination-divider" /></>}
            {actions && (
                <button
                    className={`pagination-button edit-mode-button${editMode ? " edit-mode-active" : ""}`}
                    onClick={() => { setEditMode(e => !e); if (editMode) table.resetRowSelection(); }}
                >
                    ✎ Edit
                </button>
            )}
            <span style={{ flex: 1 }} />
            {actions && editMode && selectedCount > 0 ? (
                <>
                    <span className="pagination-info">{selectedCount} selected</span>
                    <button className="pagination-button deselect-button" onClick={() => table.resetRowSelection()}>
                        ✕ Deselect
                    </button>
                    <span className="pagination-divider" />
                    {actions.map(action => (
                        <button
                            key={action.label}
                            className="pagination-button action-button"
                            onClick={() => { action.onClick(selectedRows); table.resetRowSelection(); }}
                        >
                            {action.label}
                        </button>
                    ))}
                </>
            ) : (
                <>
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
                </>
            )}
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
