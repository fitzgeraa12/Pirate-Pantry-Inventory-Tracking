import React from "react";
import ReactDOM from "react-dom";
import { Spinner } from "../misc/misc";
import { API, type Product } from "../API";
import { useCart } from "../misc/CartContext";
import { parseSearch, type SortBy, type SortDir } from "../misc/searchParser";
import "./PantryGrid.css";

const PAGE_SIZE = 18;

export default function PantryView({searchTerm, sortBy, sortDir, refreshKey}: {searchTerm: string, sortBy: SortBy, sortDir: SortDir, refreshKey?: number}): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, setProducts] = React.useState<Array<Product>>([]);
    const [isLoading, setIsLoading] = React.useState(false);
    const [page, setPage] = React.useState(1);
    const [totalPages, setTotalPages] = React.useState(1);
    const { addToCart, removeFromCart, cart } = useCart();
    const [slotEl, setSlotEl] = React.useState<HTMLElement | null>(null);

    React.useEffect(() => {
        setSlotEl(document.getElementById("pagination-slot"));
    }, []);

    // Track previous filter/sort to detect when page should reset to 1
    const prevFilterRef = React.useRef({ searchTerm, sortBy, sortDir });

    const parsed = React.useMemo(() => parseSearch(searchTerm), [searchTerm]);

    React.useEffect(() => {
        if (parsed.error) return;

        const prev = prevFilterRef.current;
        const filterChanged = prev.searchTerm !== searchTerm || prev.sortBy !== sortBy || prev.sortDir !== sortDir;
        prevFilterRef.current = { searchTerm, sortBy, sortDir };

        const effectivePage = filterChanged ? 1 : page;
        if (filterChanged) setPage(1);

        let cancelled = false;
        setIsLoading(true);
        api!.get_products({ ...parsed, page: effectivePage, page_size: PAGE_SIZE, sort_by: sortBy, sort_dir: sortDir }).then((prods) => {
            if (cancelled) return;
            setProducts(prods.data);
            setTotalPages(prods.total_pages);
            setIsLoading(false);
        });
        return () => { cancelled = true; };
    }, [searchTerm, page, sortBy, sortDir, api, refreshKey]);

    return (
        <div className="pantry-grid-outer">
            {parsed.error ? (
                <div className="pantry-grid-error">{parsed.error}</div>
            ) : isLoading ? (
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
            {totalPages > 1 && slotEl && ReactDOM.createPortal(
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
                </div>,
                slotEl
            )}
        </div>
    );
}

function TagsOverflow({ tags }: { tags: string[] }) {
    const [pos, setPos] = React.useState<{ top: number; left: number } | null>(null);
    const btnRef = React.useRef<HTMLSpanElement>(null);
    const extra = tags.length - 2;

    function show() {
        if (btnRef.current) {
            const r = btnRef.current.getBoundingClientRect();
            setPos({ top: r.bottom + 6, left: r.left });
        }
    }
    function hide() { setPos(null); }

    return (
        <span
            ref={btnRef}
            className="pantry-card-tag pantry-card-tag--more"
            onMouseEnter={show}
            onMouseLeave={hide}
        >
            +{extra}
            {pos && ReactDOM.createPortal(
                <div
                    className="pantry-card-tags-popover"
                    style={{ top: pos.top, left: pos.left }}
                    onMouseEnter={show}
                    onMouseLeave={hide}
                >
                    {tags.slice(2).map(tag => (
                        <span key={tag} className="pantry-card-tag">{tag}</span>
                    ))}
                </div>,
                document.body
            )}
        </span>
    );
}

function ProductCard({ product, cartQty, onAdd, onRemove }: {
    product: Product;
    cartQty: number;
    onAdd: () => void;
    onRemove: () => void;
}) {
    const outOfStock = product.quantity === 0;
    const overflow = product.tags.length > 2;
    const visibleTags = product.tags.slice(0, 2);
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
                    <div className="pantry-card-tags">
                        {visibleTags.map(tag => (
                            <span key={tag} className="pantry-card-tag">{tag}</span>
                        ))}
                        {overflow && <TagsOverflow tags={product.tags} />}
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

