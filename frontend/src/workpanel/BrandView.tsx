import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Brand } from "../API";
import { createColumnHelper } from "@tanstack/react-table";

const helper = createColumnHelper<Brand>();
export default function BrandView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [brands, set_brands] = React.useState<Optional<Array<Brand>>>(null);

    React.useEffect(() => {
        api!.brands().then((brnds) => {
            set_brands(brnds.data);
        })
    }, [])
    
    return (
        <TableView data={brands} column_meta={{
            meta: {
                name: { header: "Name" },
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
            order: ["name", "actions"],
        }}></TableView>
    );
}
