import './StudentFacing.css'
import Titled from "../misc/Titled";
import { useState } from 'react';
import { useContext } from 'react'; 
import ProductView from '../worker/views/ProductView';
import { useCart } from "../misc/CartContext"; 
import { AuthContext } from '../auth/AuthContext';

function StudentFacing() {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount} = useCart();
    const auth = useContext(AuthContext);
    if (!auth) return null;

    return (
        <Titled title="Checkout"> 
            <div id= "container"> 
                <div id ="header"> 
                    <div id = "title"> Pirate Pantry Checkout</div>                              
        
                             
                    <div id= "header-top-right">

                        <button id="checkout" className="header-button">Checkout</button>
                        <button id= "log-out" className="header-button"
                            onClick={(auth.logout)}>Log Out</button>
                    </div>
                </div>
                <div id= "body-header">
                    <div className= "cart-icon">
                        🛒   
                        <span className="cart-badge">{getCartCount()}</span>
                    </div>
                </div>
                <div id="body">
                    <ProductView searchTerm={searchTerm}/>
                </div>
            </div>
        </Titled>
    );
}

export default StudentFacing;
