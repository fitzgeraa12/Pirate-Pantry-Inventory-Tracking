import './StudentFacing.css'
import Titled from "../misc/Titled";
import { useState } from 'react';
import { useContext } from 'react'; 
import ProductView from '../worker/views/ProductView';
import { useCart } from "../misc/CartContext"; 
import { AuthContext } from '../auth/AuthContext';

function StudentFacing() {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount} = useCart().unwrap();
    const auth = useContext(AuthContext);
    if (auth.is_none()) return null;

    return (
<<<<<<< HEAD
        <Titled title="Checkout"> 
            <div id= "container"> 
                <div id ="header"> 
                    <div id = "title"> Pirate Pantry Checkout</div>                              
                        <input // search bar
=======
        <Titled title="Pirate Pantry Checkout">
            <div id="container">
                <div id="header">
                    <div id="title">Pirate Pantry Checkout</div>
                    <input // search bar
>>>>>>> 6d2a8be76e93ce4d10a7f6a784efbbe61dce90f0
                        type="text"
                        placeholder="Search for items..."
                        value={searchTerm}
                        onChange={(e)=> setSearchTerm(e.target.value)}
<<<<<<< HEAD
                        />                             
=======
                    />
>>>>>>> 6d2a8be76e93ce4d10a7f6a784efbbe61dce90f0
                    <div id= "header-top-right">
                        <button id="checkout" className="header-button">Checkout</button>
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
                    <ProductView searchTerm={searchTerm}/>
                </div>
            </div>
        </Titled>
    );

    // return (
    //     <Titled title="Pirate Pantry Checkout">
    //         <input // search bar
    //             type="text"
    //             placeholder="Search for items..."
    //             value={searchTerm}
    //             onChange={(e)=> setSearchTerm(e.target.value)}
    //         />
    //                 <div id= "header-top-right">

    //                     <button id="checkout" className="header-button">Checkout</button>
    //                     <button id= "log-out" className="header-button"
    //                         onClick={(auth.logout)}>Log Out</button>
    //                 </div>
    //             </div>
    //             <div id= "body-header">
    //                 <div className= "cart-icon">
    //                     🛒   
    //                     <span className="cart-badge">{getCartCount()}</span>
    //                 </div>
    //             </div>
    //             <div id="body">
    //                 <ProductView searchTerm={searchTerm}/>
    //             </div>
    //         </div>
    //     </Titled>
    // );
}

export default StudentFacing;
