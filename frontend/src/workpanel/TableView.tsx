import React from "react";
import { API, type Product } from "../API";
import type { Optional } from "../misc/misc";

export default function TableView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [page_no, set_page_no] = React.useState(1);
    const [products, set_products] = React.useState<Optional<Array<Product>>>(null);

    React.useEffect(() => {
        api!.products().then((prods) => {
            set_products(prods);
        })
    }, [])

    if (!products) {
        return <div id="table-view">Loading...</div>;
    }
    
    return (
        <div id="table-view">
            {products.map((product) => (
                <div key={product.id}>
                    {product.name}
                </div>
            ))}
        </div>
    );
}