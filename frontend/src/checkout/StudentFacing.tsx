import './StudentFacing.css'
import Titled from "../misc/Titled";
import React, { useState } from 'react';
import BrandView from "../workpanel/BrandView";
import TagView from "../workpanel/TagsView";
import SettingsView from "../workpanel/SettingsView";
import PantryView from './PantryView';
import { useCart } from "../misc/CartContext"; 
import { useTheme } from "../misc/useTheme";
import { API, type User } from "../API";
import { useNavigate } from 'react-router-dom';


type Panel = "products" | "brands" | "tags" | "settings";

function PanelContent({ panel, searchTerm }: { panel: Panel, searchTerm: string }): React.ReactNode {
    switch (panel) {
        case "products":  return <PantryView searchTerm={searchTerm} />;
        case "brands":    return <BrandView />;
        case "tags":      return <TagView />;
        case "settings":  return <SettingsView />;
    }
}

export default function StudentFacing(): React.ReactNode {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount, clearCart} = useCart();
    // const navigate = useNavigate();
    // if (auth.is_none()) return null;

    const [_theme, _cycleTheme] = useTheme();
    const [panel, _setPanel] = React.useState<Panel>("products");
    const [_user, setUser] = React.useState<User | null>(null);
    const navigate = useNavigate();
    const api = React.useContext(API.Context);

    React.useEffect(() => {
        api!.get_user().then(u => { if (u) setUser(u); });
    }, [api]);    

    return (
        <Titled title="Pantry">
            <div id="container">
                <div id="header">
                    <div id="title">Pirate Pantry</div>
                    <input // search bar
                        type="text"
                        placeholder="Search for items..."
                        value={searchTerm}
                        onChange={(e)=> setSearchTerm(e.target.value)}
                    />
                    <div id= "header-top-right">
                        <button onClick={ () => navigate("/checkout")}>Checkout</button>
                        {/* <button id= "log-out" className="header-button"
                            onClick={(auth.expect("no augh in student facing").logout)}>Log Out
                        </button> */}
                    </div>
                </div>
                <div id="body-header">
                    <div className="cart-icon">
                        🛒
                        <span className="cart-badge">{getCartCount()}</span>
                        <button onClick={ () => clearCart()}> Clear Cart </button>
                    </div>
                </div>
                <div id="body">
                    <PanelContent panel={panel} searchTerm={searchTerm} />
                </div>
            </div>
        </Titled>
    );

};


