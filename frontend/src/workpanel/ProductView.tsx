import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type Product } from "../API";
import { createColumnHelper } from "@tanstack/react-table";

const helper = createColumnHelper<Product>();
export default function ProductView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, set_products] = React.useState<Optional<Array<Product>>>(null);

    React.useEffect(() => {
        api!.get_products({name: "%tomato%"}).then((prods) => {
            console.log(prods.data)
            set_products(prods.data);
        })
    }, [])
    
    return (
        <TableView data={products} column_meta={{
            meta: {
                id: { header: "Id" },
                name: { header: "Name" },
                brand: { header: "Brand" },
                quantity: { header: "Quantity" },
                tags: { header: "Tags" },
                image_link: { header: "Image" },
                actions: {
                    type: "display",
                    column: helper.display({
                        id: "actions",
                        cell: ({ }) => (
                            <>
                                <button
                                    className="table-entry-button"
                                    // onClick={() => addToCart(row.original.id, row.original.name, row.original.quantity)}
                                >
                                    Edit
                                </button>
                                <button
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
            order: ["id", "image_link", "name", "brand", "quantity", "tags", "actions"],
        }}></TableView>
    );
}
