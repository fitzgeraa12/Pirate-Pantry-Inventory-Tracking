import React from "react";
import ReactDOM from "react-dom";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { Spinner } from "../misc/misc";
import { API, type Product } from "../API";
import "./AddItem.css";
import { useSearchParams } from "react-router-dom";
import { useLocation } from "react-router-dom";
import { parseSearch, SORT_LABELS, type SortBy, type SortDir } from "../misc/searchParser";import SortDropdown from '../misc/SortDropdown';

function DeleteConfirmModal({ product, onConfirm, onCancel }: { product: Product; onConfirm: () => Promise<void>; onCancel: () => void }): React.ReactNode {
    const [loading, setLoading] = React.useState(false);

    async function handleConfirm() {
        setLoading(true);
        try {
            await onConfirm();
        } finally {
            setLoading(false);
        }
    }

    return ReactDOM.createPortal(
        <div className="add-item-overlay" onClick={loading ? undefined : onCancel}>
            <div className="add-item-modal" style={{ width: 340 }} onClick={e => e.stopPropagation()}>
                <div className="add-item-modal-header">
                    <h2 className="add-item-modal-title">Delete Product</h2>
                    <button className="add-item-close" onClick={onCancel} disabled={loading}>✕</button>
                </div>
                <div className="add-item-form">
                    <p style={{ margin: 0, fontSize: '0.92em', color: 'var(--chrome-text)' }}>
                        Delete <strong>{product.name}</strong>? This cannot be undone.
                    </p>
                    <div className="add-item-actions">
                        <button className="add-item-btn add-item-btn--secondary" onClick={onCancel} disabled={loading}>Cancel</button>
                        <button
                            className="add-item-btn add-item-btn--primary"
                            style={{ backgroundColor: '#c0392b', borderColor: '#c0392b', color: '#fff' }}
                            onClick={handleConfirm}
                            disabled={loading}
                        >{loading ? <Spinner className="spinner--sm" /> : "Delete"}</button>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
}

export default function ProductView({ onEdit }: { onEdit?: (product: Product) => void }): React.ReactNode {
    const api = React.useContext(API.Context);
    const [products, set_products] = React.useState<Optional<Array<Product>>>(null);
    const [deletingProduct, setDeletingProduct] = React.useState<Product | null>(null);
    const [isLoading, setIsLoading] = React.useState(false);
    const [inputValue, setInputValue] = React.useState("");
    const [debouncedInput, setDebouncedInput] = React.useState("");
    const [page, setPage] = React.useState(1);
    const [total, setTotal] = React.useState(0);
    const [totalPages, setTotalPages] = React.useState(1);
    const [sortBy, setSortBy] = React.useState<SortBy>('name');
    const [sortDir, setSortDir] = React.useState<SortDir>('asc');
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;
    const [searchParams] = useSearchParams();
    const searchRef = React.useRef<HTMLInputElement>(null);
    const location = useLocation();
    const refresh = location.state?.refresh;

    const toggleSort = (field: SortBy) => {
        if (sortBy === field) { setSortDir(d => d === 'asc' ? 'desc' : 'asc'); }
        else { setSortBy(field); setSortDir('asc'); }
    };

    React.useEffect(() => {
        const timer = setTimeout(() => { setDebouncedInput(inputValue.trim()); setPage(1); }, 300);
        return () => clearTimeout(timer);
    }, [inputValue]);

    const parsed = React.useMemo(() => parseSearch(debouncedInput), [debouncedInput]);

    const prevFilterRef = React.useRef({ debouncedInput, sortBy, sortDir });

    React.useEffect(() => {
        if (parsed.error) return;
        const prev = prevFilterRef.current;
        const filterChanged = prev.debouncedInput !== debouncedInput || prev.sortBy !== sortBy || prev.sortDir !== sortDir;
        prevFilterRef.current = { debouncedInput, sortBy, sortDir };
        const effectivePage = filterChanged ? 1 : page;
        if (filterChanged) setPage(1);

        const wasFocused = document.activeElement === searchRef.current;
        let cancelled = false;
        setIsLoading(true);
        api!.get_products({ ...parsed, page: effectivePage, page_size: pageSize, sort_by: sortBy, sort_dir: sortDir }).then((prods) => {
            if (cancelled) return;
            set_products(prods.data);
            setTotal(prods.total);
            setTotalPages(prods.total_pages);
            setIsLoading(false);
            if (wasFocused) searchRef.current?.focus();
        }).catch((error) => {
            if (cancelled) return;
            console.error("Failed to load products:", error);
            set_products(null);
            setIsLoading(false);
        });
        return () => { cancelled = true; };
    }, [debouncedInput, page, sortBy, sortDir, refresh]);

    const portalTarget = document.getElementById('header-toolbar');

    const toolbar = (
        <div className="table-toolbar">
            <input
                ref={searchRef}
                className="table-search"
                type="search"
                placeholder="Search… id:110, name:, brand:, tag:, qty>N"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
            />
            <SortDropdown sortBy={sortBy} sortDir={sortDir} onToggle={toggleSort} />
            {parsed.error && <span className="table-search-error">{parsed.error}</span>}
        </div>
    );
    
    return (
        <>
        {portalTarget && ReactDOM.createPortal(toolbar, portalTarget)}
        <TableView data={products} isLoading={isLoading} pageSize={pageSize}
            serverPagination={{ page, total, totalPages, onPageChange: setPage }}
            column_meta={{
            meta: {
                id: { header: "Id" },
                name: { header: "Name" },
                brand: { header: "Brand" },
                quantity: { header: "Quantity" },
                tags: { header: "Tags", cell: (val: Array<string>) => <>{val.join(", ")}</> },

                actions: {
                    type: "display",
                    column: {
                        id: "actions",
                        header: "",
                        meta: { shrink: true },
                        cell: (info: any) => {
                            const row: Product = info.row.original;
                            return (
                                <div style={{ display: 'flex', gap: 6 }}>
                                    <button className="pagination-button action-button" onClick={() => onEdit?.(row)}>Edit</button>
                                    <button
                                        className="pagination-button"
                                        style={{ color: '#e05555', borderColor: '#e05555' }}
                                        onClick={() => setDeletingProduct(row)}
                                    >Delete</button>
                                </div>
                            );
                        },
                    },
                },
            },
            order: ["id", "name", "brand", "quantity", "tags", "actions"],
        }} />
        {deletingProduct && (
            <DeleteConfirmModal
                product={deletingProduct}
                onCancel={() => setDeletingProduct(null)}
                onConfirm={async () => {
                    await api!.delete_products([deletingProduct.id]);
                    setDeletingProduct(null);
                    set_products(prev => prev?.filter(p => p.id !== deletingProduct.id) ?? prev);
                }}
            />
        )}
        </>
    );
}
