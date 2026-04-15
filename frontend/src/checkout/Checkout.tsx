import React from "react";
import { useNavigate } from "react-router-dom";
import { useCart } from "../misc/CartContext";
import { API } from "../API";

function Checkout() {
    const navigate = useNavigate();
    const { cart = [], clearCart } = useCart() || {};
    const api = React.useContext(API.Context)!;

    const handleConfirm = async () => {
        if (cart.length === 0) {
            alert("Cart is empty!");
            return;
        }

        try {
            const quantities = await api.checkout(
                cart.map(item => ({ id: item.id, amount: item.quantity }))
            );

            console.log("Updated quantities:", quantities);
            clearCart();
            alert("Checkout successful!");
            navigate("/pantry");

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
        }
    };

    const handleBack = () => {
        navigate("/pantry");
    };

    return (
        <div id= "container">
            <div id = "header">
                <div id ="title">Checkout</div>

                <div id= "header-top-right">
                    <button className="header-button" onClick={handleBack}>
                        Back to Cart
                    </button>
                </div>
            </div>
            <div>
                Help
            </div>
            <div id="body">
                <div id="view">

                    <div id="body-header">
                        <span>Checkout</span>
                    </div>
                    <div id="checkout-container">
                        {cart.length === 0 ?(
                            <div>Your cart is empty. </div>
                        ) : (
                            <>
                                {cart.map((item) =>(
                                    <div className="checkout-item" key={item.id}>
                                        <span className="checkout-item-name">
                                            {item.name}
                                        </span>
                                        <span> </span> 
                                        <span className="checkout-item-quantity">
                                            x{item.quantity}
                                        </span>
                                    </div>
                                ))}
                                <div id="checkout-summary">
                                    <span>
                                        Total Items:{" "}
                                        {cart.reduce((total, item) => total + item.quantity, 0)}
                                    </span>

                                    <button id="confrim-checkout" onClick={handleConfirm}>
                                        Confirm Checkout
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Checkout;