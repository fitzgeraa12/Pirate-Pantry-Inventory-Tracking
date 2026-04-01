import React from "react";
import type { Optional } from "../misc/misc";
import { createColumnHelper, flexRender, getCoreRowModel, useReactTable, type ColumnDef, type RowData } from "@tanstack/react-table";
import './TableView.css'

type BoxedPrimitive<T> = { value: T };
type RowType<T> = T extends object ? T : BoxedPrimitive<T>;
function normalize_data<T>(data: Array<T>): Array<RowType<T>> {
    if (data.length === 0) return [];
    return (typeof data[0] === "object" 
        ? data 
        : data.map(v => ({ value: v }))
    ) as Array<RowType<T>>;
}

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
            ...(entry.cell && {
                cell: (info) => entry.cell!(info.getValue() as T[keyof T], info.row.original),
            }),
        });
    }) as ColumnDef<T, unknown>[];
}

export default function TableView<
    T,
    E extends string = never,
    M extends FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E> 
        = FieldMetaMap<RowType<T>> & ExtraMetaMap<RowType<T>, E>
>({ data, column_meta }: {
    data: Optional<Array<T>>;
    column_meta: {
        meta: M;
        order?: Array<keyof M>;
    };
}): React.ReactNode {
    const columns = React.useMemo(
        () => build_cols(column_meta.meta as TableMeta<T>["meta"], column_meta.order as string[]),
        [column_meta]
    );

    const table = useReactTable({
        data: data ?? [],
        columns,
        getCoreRowModel: getCoreRowModel(),
    });

    const [page_no, set_page_no] = React.useState(1);
    
    return data ? (
        <div className="table-view-wrapper">
            <table className="table-view">
                <thead className="table-view-header">
                    {table.getHeaderGroups().map(headerGroup => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map(header => (
                                <th className="table-view-header-cell" key={header.id}>
                                    {flexRender(
                                        header.column.columnDef.header,
                                        header.getContext()
                                    )}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody className="table-view-body">
                    {table.getRowModel().rows.map(row => (
                        <tr key={row.id}>
                            {row.getVisibleCells().map(cell => (
                                <td className="table-view-data-cell" key={cell.id}>
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
        </div>
    ) : (
        <>Loading...</>
    );
}
