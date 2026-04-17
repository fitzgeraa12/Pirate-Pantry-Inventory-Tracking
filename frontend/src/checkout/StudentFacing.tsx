import './StudentFacing.css'
import Titled from "../misc/Titled";
import React, { useState } from 'react';
import BrandView from "../workpanel/BrandView";
import TagView from "../workpanel/TagsView";
import SettingsView from "../workpanel/SettingsView";
import PantryView from './PantryView';
import CheckoutPanel from './CheckoutPanel';

const THEME_LABELS = { light: "☀  Light", dark: "🌙  Dark", auto: "⊙  System" };
import { useCart } from "../misc/CartContext"; 
import { useTheme } from "../misc/useTheme";
import { API, type User } from "../API";
import { useNavigate } from 'react-router-dom';

function initials(email: string): string {
    const name = email.split("@")[0];
    const parts = name.split(/[._-]/).filter(Boolean);
    if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
    return name.slice(0, 2).toUpperCase();
}

function UserMenu({ user }: { user: User }): React.ReactNode {
    const [open, setOpen] = React.useState(false);
    const ref = React.useRef<HTMLDivElement>(null);
    const navigate = useNavigate();
    const api = React.useContext(API.Context);

    React.useEffect(() => {
        function onClickOutside(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        }
        document.addEventListener("mousedown", onClickOutside);
        return () => document.removeEventListener("mousedown", onClickOutside);
    }, []);

    function logOut() {
        api!.logout();
        navigate("/");
    }

    const picture = localStorage.getItem("user-picture");

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

function ReportModal({ isOpen, onClose, onSubmit }: { isOpen: boolean, onClose: () => void, onSubmit: (message: string) => void }): React.ReactNode {
    const [message, setMessage] = React.useState("");

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (message.trim()) {
            onSubmit(message.trim());
            setMessage("");
            onClose();
        }
    }

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Report an Issue</h3>
                <form onSubmit={handleSubmit}>
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Describe the issue you encountered..."
                        rows={4}
                        maxLength={1000}
                        required
                    />
                    <div className="modal-buttons">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit" disabled={!message.trim()}>Submit Report</button>
                    </div>
                </form>
            </div>
        </div>
    );
}


type Panel = "products" | "brands" | "tags" | "settings" | "checkout";

function PanelContent({ panel, searchTerm }: { panel: Panel, searchTerm: string }): React.ReactNode {
    switch (panel) {
        case "products":  return <PantryView searchTerm={searchTerm} />;
        case "brands":    return <BrandView />;
        case "tags":      return <TagView />;
        case "settings":  return <SettingsView />;
        case "checkout":  return <CheckoutPanel />;
    }
}

export default function StudentFacing(): React.ReactNode {
    const [searchTerm, setSearchTerm] = useState<string>("");
    const {getCartCount, clearCart} = useCart();
    // const navigate = useNavigate();
    // if (auth.is_none()) return null;

    const [theme, cycleTheme] = useTheme();
    const [panel, setPanel] = React.useState<Panel>("products");
    const [user, setUser] = React.useState<User | null>(null);
    const [showReportModal, setShowReportModal] = React.useState(false);
    const navigate = useNavigate();
    const api = React.useContext(API.Context);

    React.useEffect(() => {
        api!.get_user().then(u => { if (u) setUser(u); });
    }, [api]);

    function handleReportSubmit(message: string) {
        api!.submit_report(message).catch(err => {
            console.error("Failed to submit report:", err);
            alert("Failed to submit report. Please try again.");
        });
    }    

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
                        <button className="header-button" onClick={cycleTheme} data-active={theme !== "auto" ? "" : undefined}>
                            Theme: {THEME_LABELS[theme]}
                        </button>
                        {user && (
                            <button className="header-button" onClick={() => navigate("/workpanel")}>Workpanel</button>
                        )}
                        {user && <UserMenu user={user} />}
                    </div>
                </div>
                <div id="body">
                    <div id="body-left">
                        <span className="body-left-section-label">Pantry</span>
                        <button className="body-left-button body-left-sub-button" onClick={() => setPanel("products")} data-active={panel === "products" ? "" : undefined}>Products</button>
                        <button className="body-left-button body-left-sub-button" onClick={() => setPanel("brands")} data-active={panel === "brands" ? "" : undefined}>Brands</button>
                        <button className="body-left-button body-left-sub-button" onClick={() => setPanel("tags")} data-active={panel === "tags" ? "" : undefined}>Tags</button>
                        <div className="body-left-spacer" />
                        <hr className="body-left-divider" />
                        <button className="body-left-button" onClick={() => setPanel("checkout")} data-active={panel === "checkout" ? "" : undefined}>
                            🛒 Checkout ({getCartCount()})
                        </button>
                        <button className="body-left-button" onClick={() => setPanel("settings")} data-active={panel === "settings" ? "" : undefined}>Settings</button>
                        <button className="body-left-button" onClick={() => setShowReportModal(true)}>Report Issue</button>
                        <div className="body-left-spacer" />
                        <hr className="body-left-divider" />
                        <span className="body-left-section-label">Appearance</span>
                        <button className="body-left-button body-left-button--sm" onClick={cycleTheme} data-active={theme !== "auto" ? "" : undefined}>
                            Theme: {THEME_LABELS[theme]}
                        </button>
                    </div>
                    <div className="panel-container">
                        {panel === "products" && (
                            <div className="search-bar-container">
                                <input
                                    type="text"
                                    placeholder="Search for items..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="search-bar"
                                />
                            </div>
                        )}
                        <PanelContent panel={panel} searchTerm={searchTerm} />
                    </div>
                </div>
                <ReportModal
                    isOpen={showReportModal}
                    onClose={() => setShowReportModal(false)}
                    onSubmit={handleReportSubmit}
                />
            </div>
        </Titled>
    );

};


