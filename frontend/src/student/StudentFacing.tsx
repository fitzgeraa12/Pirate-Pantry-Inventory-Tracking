import './StudentFacing.css'
import Titled from "../misc/Titled";
import { useState } from 'react';
import { useContext } from 'react'; 
import PantryView from './PantryView';
import { useCart } from "../misc/CartContext"; 
import { AuthContext } from '../auth/AuthContext';
import { useNavigate } from 'react-router-dom';

function StudentFacing() {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount} = useCart();
    const auth = useContext(AuthContext);
    const navigate = useNavigate();
    if (auth.is_none()) return null;

    return (
        <Titled title="Checkout">
            <div id="container">
                <div id="header">
                    <div id="title">
                        <img 
                            src="/workspaces/Pirate-Pantry-Inventory-Tracking/Pantry_logo.jpg"
                            alt="Pantry Logo"
                            className="header-logo"
                        />
                        <span>Pirate Pantry</span>
                    </div>
                    <input // search bar
                        type="text"
                        placeholder="Search for items..."
                        value={searchTerm}
                        onChange={(e)=> setSearchTerm(e.target.value)}
                        />  
                    <div id= "header-top-right">
                        <button onClick={ () => navigate("/checkout")}>Checkout</button>
                        <button id= "log-out" className="header-button"
                            onClick={(auth.expect("no augh in student facing").logout)}>Log Out
                        </button>
                    </div>
                </div>
                <div id="body-header">
                    <div className="cart-icon">
                        🛒
                        <span className="cart-badge">{getCartCount()}</span>
                    </div>
                </div>
                <div id="body">
                    <PantryView searchTerm={searchTerm}/>
                </div>
            </div>
        </Titled>
    );

}

export default StudentFacing;
