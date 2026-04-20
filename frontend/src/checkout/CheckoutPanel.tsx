import React from "react";
import ReactDOM from "react-dom";
import { useCart } from "../misc/CartContext";
import { API } from "../API";
import { Spinner } from "../misc/misc";
import "../workpanel/AddItem.css";

export default function CheckoutPanel({ onClose, onSuccess }: { onClose: () => void; onSuccess?: () => void }): React.ReactNode {
    const { cart = [], clearCart } = useCart() || {};
    const api = React.useContext(API.Context)!;
    const [loading, setLoading] = React.useState(false);

    const handleConfirm = async () => {
        setLoading(true);
        try {
            await api.checkout(
                cart.map(item => ({ id: item.id, amount: item.quantity }))
            );
            clearCart();
            onSuccess?.();
            onClose();
        } catch (error: any) {
            const data = error?.response?.data;
            if (data?.error === 'not_enough_stock' && data?.out_of_stock?.length) {
                const names = data.out_of_stock.map((p: any) =>
                    `${p.name} (requested ${p.requested}, only ${p.available} available)`
                ).join('\n');
                alert(`Some items are out of stock:\n\n${names}`);
            } else {
                alert("Checkout failed. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    return ReactDOM.createPortal(
        <div className="add-item-overlay" onMouseDown={(e) => { if (!loading && e.target === e.currentTarget) onClose(); }}>
            <div className="add-item-modal checkout-modal">
                <div className="add-item-modal-header">
                    <h3 className="add-item-modal-title">Checkout</h3>
                    <button className="add-item-close" onClick={onClose} disabled={loading} aria-label="Close">✕</button>
                </div>

                {cart.length === 0 ? (
                    <div className="checkout-modal-empty">
                        Cart is empty.
                    </div>
                ) : (
                    <>
                        <div className="checkout-modal-items">
                            {cart.map(item => (
                                <div key={item.id} className="checkout-modal-item">
                                    <span className="checkout-modal-item-name">{item.name}</span>
                                    <span className="checkout-modal-item-qty">×{item.quantity}</span>
                                </div>
                            ))}
                        </div>
                        <div className="checkout-modal-footer">
                            <span className="checkout-modal-total">Total: {totalItems} item{totalItems !== 1 ? 's' : ''}</span>
                            <div className="add-item-actions">
                                <button
                                    className="add-item-btn add-item-btn--secondary"
                                    onClick={() => clearCart()}
                                    disabled={loading}
                                >
                                    Clear Cart
                                </button>
                                <button
                                    className="add-item-btn add-item-btn--primary"
                                    onClick={handleConfirm}
                                    disabled={loading}
                                >
                                    {loading ? <Spinner className="spinner--sm" /> : "Confirm"}
                                </button>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>,
        document.body
    );
}
