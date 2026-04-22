import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Brand } from "../API";

export default function BrandView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [brands, setBrands] = React.useState<Optional<Array<Brand>>>(null);
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;

    React.useEffect(() => {
        api!.get_brands({ page_size: 99999 }).then(b => {
            const sortedBrands = b.data.sort((a, b) => a.name.localeCompare(b.name));
            setBrands(sortedBrands);
        });
    }, []);

    return (
        <TableView data={brands} pageSize={pageSize} column_meta={{
            meta: {
                name: { header: "Name" },
            },
            order: ["name"],
        }} />
    );
}
