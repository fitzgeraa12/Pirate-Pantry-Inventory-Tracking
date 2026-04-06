import { useNavigate } from "react-router-dom";
import { useCart } from "../misc/CartContext";

function Checkout() {
    const navigate = useNavigate();
    const { cart = [], clearCart } = useCart() || {};

    const handleConfirm = () => {
        // more expansion possible ie database modification
        clearCart(); // empty cart
        alert("Checkout successful!");
        navigate("/"); // return to main student page
    };

    const handleBack = () => {
        navigate("/");
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