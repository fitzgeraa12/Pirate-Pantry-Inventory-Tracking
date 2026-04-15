import React from "react";
import { Spinner } from "../misc/misc";
import { API, type Product } from "../API";
import { useCart } from "../misc/CartContext";
import "./PantryGrid.css";

const PAGE_SIZE = 20;

export default function PantryView({searchTerm}: {searchTerm: string}): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, setProducts] = React.useState<Array<Product>>([]);
    const [isLoading, setIsLoading] = React.useState(false);
    const [page, setPage] = React.useState(1);
    const [totalPages, setTotalPages] = React.useState(1);
    const { addToCart, removeFromCart, cart } = useCart();

    // Reset to page 1 when search changes
    React.useEffect(() => {
        setPage(1);
    }, [searchTerm]);

    React.useEffect(() => {
        setIsLoading(true);
        api!.get_products({ search: searchTerm.trim() || undefined, page, page_size: PAGE_SIZE }).then((prods) => {
            setProducts(prods.data);
            setTotalPages(prods.total_pages);
            setIsLoading(false);
        });
    }, [searchTerm, page, api]);

    return (
        <div className="pantry-grid-outer">
            {isLoading ? (
                <div className="pantry-grid-loading"><Spinner /></div>
            ) : products.length === 0 ? (
                <div className="pantry-grid-empty">No products found.</div>
            ) : (
                <div className="pantry-grid">
                    {products.map(product => (
                        <ProductCard
                            key={product.id}
                            product={product}
                            cartQty={cart.find(c => c.id === product.id)?.quantity ?? 0}
                            onAdd={() => addToCart(product.id, product.name, product.quantity)}
                            onRemove={() => removeFromCart(product.id)}
                        />
                    ))}
                </div>
            )}
            {totalPages > 1 && (
                <div className="pantry-pagination">
                    <button
                        className="pantry-pagination-btn"
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page <= 1}
                    >← Prev</button>
                    <span className="pantry-pagination-info">{page} / {totalPages}</span>
                    <button
                        className="pantry-pagination-btn"
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page >= totalPages}
                    >Next →</button>
                </div>
            )}
        </div>
    );
}

function ProductCard({ product, cartQty, onAdd, onRemove }: {
    product: Product;
    cartQty: number;
    onAdd: () => void;
    onRemove: () => void;
}) {
    const outOfStock = product.quantity === 0;
    const [tagsExpanded, setTagsExpanded] = React.useState(false);
    const overflow = product.tags.length > 2;
    const visibleTags = tagsExpanded ? product.tags : product.tags.slice(0, 2);
    return (
        <div className={`pantry-card${outOfStock ? " pantry-card--oos" : ""}`}>
            <div className="pantry-card-image">
                {product.image_link
                    ? <img src={product.image_link} alt={product.name} />
                    : <div className="pantry-card-image-placeholder">📦</div>
                }
            </div>
            <div className="pantry-card-body">
                <div className="pantry-card-name">{product.name}</div>
                {product.brand && <div className="pantry-card-brand">{product.brand}</div>}
                {product.tags.length > 0 && (
                    <div className={`pantry-card-tags${tagsExpanded ? " pantry-card-tags--expanded" : ""}`}>
                        {visibleTags.map(tag => (
                            <span key={tag} className="pantry-card-tag">{tag}</span>
                        ))}
                        {overflow && (
                            <span
                                className="pantry-card-tag pantry-card-tag--more"
                                onClick={(e) => { e.stopPropagation(); setTagsExpanded(v => !v); }}
                            >{tagsExpanded ? "−" : `+${product.tags.length - 2}`}</span>
                        )}
                    </div>
                )}
                <div className={`pantry-card-qty${outOfStock ? " pantry-card-qty--oos" : ""}`}>
                    {outOfStock ? "Out of stock" : `${product.quantity} in stock`}
                </div>
            </div>
            <div className="pantry-card-actions">
                <button className="pantry-card-btn pantry-card-btn--remove" onClick={onRemove} disabled={cartQty === 0}>−</button>
                {cartQty > 0 && <span className="pantry-card-cart-qty">{cartQty}</span>}
                <button className="pantry-card-btn pantry-card-btn--add" onClick={onAdd} disabled={outOfStock}>+</button>
            </div>
        </div>
    );
}

