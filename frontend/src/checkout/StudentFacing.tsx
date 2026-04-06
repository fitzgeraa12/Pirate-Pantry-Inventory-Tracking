import './StudentFacing.css'
import Titled from "../misc/Titled";
import React, { useState, useContext, useEffect } from 'react';
import BrandView from "../workpanel/BrandView";
import TagView from "../workpanel/TagsView";
import UserView from "../workpanel/UserView";
import SettingsView from "../workpanel/SettingsView";
import PantryView from './PantryView';
import { useCart } from "../misc/CartContext"; 
import { useTheme } from "../misc/useTheme";
import { API, type User } from "../API";
import { useNavigate } from 'react-router-dom';

const THEME_LABELS = { light: "☀  Light", dark: "🌙  Dark", auto: "⊙  System" };

type Panel = "products" | "brands" | "tags" | "settings";

function initials(email: string): string {
    const name = email.split("@")[0];
    const parts = name.split(/[._-]/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
}


function UserMenu({ user }: { user: User }): React.ReactNode {
    const [open, setOpen] = React.useState(false);
    const ref = React.useRef<HTMLDivElement>(null);
    const picture = localStorage.getItem("user-picture");

    React.useEffect(() => {
        function onClickOutside(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        }
        document.addEventListener("mousedown", onClickOutside);
        return () => document.removeEventListener("mousedown", onClickOutside);
    }, []);

    function logOut() {
        localStorage.removeItem("session");
        localStorage.removeItem("user-picture");
        window.location.href = "/";
    }

    return (
        <div className="user-menu" ref={ref}>
            <button className="user-avatar" onClick={() => setOpen(o => !o)} aria-label="Account menu">
                {picture
                    ? <img src={picture} alt={user.email} className="user-avatar-img" referrerPolicy="no-referrer" />
                    : initials(user.email)
                }
            </button>
            {open && (
                <div className="user-menu-dropdown">
                    <div className="user-menu-email">{user.email}</div>
                    <div className="user-menu-badge">{user.access_level}</div>
                    <hr className="user-menu-divider" />
                    <button className="user-menu-item" onClick={logOut}>Log Out</button>
                </div>
            )}
        </div>
    );
}

function PanelContent({ panel }: { panel: Panel }): React.ReactNode {
    switch (panel) {
        case "products":  return <PantryView />;
        case "brands":    return <BrandView />;
        case "tags":      return <TagView />;
        case "settings":  return <SettingsView />;
    }
}

export default function StudentFacing(): React.ReactNode {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount} = useCart();
    // const navigate = useNavigate();
    // if (auth.is_none()) return null;

    const [theme, cycleTheme] = useTheme();
    const [panel, setPanel] = React.useState<Panel>("products");
    const [user, setUser] = React.useState<User | null>(null);
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
                    </div>
                </div>
                <div id="body">
                    <PanelContent panel={panel} />
                </div>
            </div>
        </Titled>
    );

};


