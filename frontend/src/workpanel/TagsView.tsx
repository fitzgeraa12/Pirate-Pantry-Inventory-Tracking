import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Tag } from "../API";

export default function TagView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [tags, setTags] = React.useState<Optional<Array<Tag>>>(null);
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;

    React.useEffect(() => {
        api!.get_tags({ page_size: 99999 }).then(t => setTags(t.data));
    }, []);

    return (
        <TableView data={tags} pageSize={pageSize} column_meta={{
            meta: {
                label: { header: "Label" },
            },
            order: ["label"],
        }} />
    );
}
