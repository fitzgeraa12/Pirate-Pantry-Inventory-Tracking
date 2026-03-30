import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Tag } from "../API";
import { createColumnHelper } from "@tanstack/react-table";

const helper = createColumnHelper<Tag>();
export default function TagView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [tags, set_tags] = React.useState<Optional<Array<Tag>>>(null);

    React.useEffect(() => {
        api!.tags().then((tgs) => {
            set_tags(tgs);
        })
    }, [])
    
    return (
        <TableView data={tags} column_meta={{
            meta: {
                label: { header: "Name" },
                actions: {
                    type: "display",
                    column: helper.display({
                        id: "actions",
                        cell: ({ }) => (
                            <>
                                <button
                                    style={{color: "white"}}
                                    className="table-entry-button"
                                    // onClick={() => addToCart(row.original.id, row.original.name, row.original.quantity)}
                                >
                                    Edit
                                </button>
                                <button
                                    style={{color: "white"}}
                                    className="table-entry-button"
                                    // onClick={() => removeFromCart(row.original.id)}
                                >
                                    Remove
                                </button>
                            </>
                        ),
                    }),
                },
            },
            order: ["label", "actions"],
        }}></TableView>
    );
}
