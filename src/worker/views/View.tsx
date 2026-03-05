import { flexRender, type Table } from "@tanstack/react-table";
import type { ReactNode } from "react";

interface ViewProps<T> {
    id: string,
    tbl: Table<T>,
    header_children: ReactNode,
}

function View<T>({ id, tbl, header_children }: ViewProps<T>) {
    return (
        <div id={id}>
            <div id="body-header">
                {header_children}
            </div>
            <table id="database-view">
                <thead>
                    {tbl.getHeaderGroups().map(header_group => {
                        return (
                        <tr key={header_group.id}>
                            {header_group.headers.map(header => (
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
                    {tbl.getRowModel().rows.map(row => (
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
            <div id="body-footer">
                <div id="quick-statistics">TODO: Statistics</div>
            </div>
        </div>
    );
}

export default View;
