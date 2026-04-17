import React from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../misc/CartContext";
import { API } from "../API";

export default function CheckoutPanel(): React.ReactNode {
    const navigate = useNavigate();
    const { cart = [], clearCart } = useCart() || {};
    const api = React.useContext(API.Context)!;
    const [loading, setLoading] = React.useState(false);

    const handleConfirm = async () => {
        if (cart.length === 0) {
            alert("Cart is empty!");
            return;
        }

        setLoading(true);
        try {
            const quantities = await api.checkout(
                cart.map(item => ({ id: item.id, amount: item.quantity }))
            );

            console.log("Updated quantities:", quantities);
            clearCart();
            alert("Checkout successful!");

        } catch (error: any) {
            console.error(error);
            const data = error?.response?.data;
            console.error("Server error:", data);
            if (data?.error === 'not_enough_stock' && data?.out_of_stock?.length) {
                const names = data.out_of_stock.map((p: any) =>
                    `${p.name} (requested ${p.requested}, only ${p.available} available)`
                ).join('\n');
                alert(`Some items are out of stock:\n\n${names}`);
            } else {
                alert("Checkout failed!");
            }
        } finally {
            setLoading(false);
        }
    };

    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    return (
        <div className="checkout-panel">
            <h2>Shopping Cart</h2>
            
            {cart.length === 0 ? (
                <div className="checkout-empty">
                    <p>Your cart is empty</p>
                </div>
            ) : (
                <>
                    <div className="checkout-items">
                        {cart.map(item => (
                            <div key={item.id} className="checkout-item">
                                <div className="checkout-item-info">
                                    <div className="checkout-item-name">{item.name}</div>
                                </div>
                                <div className="checkout-item-quantity">
                                    <span className="checkout-qty-label">Qty:</span>
                                    <span className="checkout-qty-value">{item.quantity}</span>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="checkout-summary">
                        <div className="checkout-summary-row">
                            <span>Total Items:</span>
                            <span>{totalItems}</span>
                        </div>
                    </div>

                    <div className="checkout-actions">
                        <button
                            className="checkout-button checkout-button-clear"
                            onClick={() => clearCart()}
                            disabled={loading}
                        >
                            Clear Cart
                        </button>
                        <button
                            className="checkout-button checkout-button-confirm"
                            onClick={handleConfirm}
                            disabled={loading || cart.length === 0}
                        >
                            {loading ? "Processing..." : "Confirm Checkout"}
                        </button>
                    </div>
                </>
            )}
        </div>
    );
}