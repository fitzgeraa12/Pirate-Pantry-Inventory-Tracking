import './StudentFacing.css'
import Titled from "../misc/Titled";
import React, { useState } from 'react';
import BrandView from "../workpanel/BrandView";
import TagView from "../workpanel/TagsView";
import SettingsView from "../workpanel/SettingsView";
import PantryView from './PantryView';
import CheckoutPanel from './CheckoutPanel';
import { SORT_LABELS, type SortBy, type SortDir } from '../misc/searchParser';
import SortDropdown from '../misc/SortDropdown';
import logo from "../images/Pantry_logo.png";


const THEME_ICONS = { light: "☀", dark: "🌙", auto: "⊙" };
const THEME_NAMES = { light: "Light", dark: "Dark", auto: "System" };
import { useCart } from "../misc/CartContext";
import { useTheme } from "../misc/useTheme";
import { API, type User } from "../API";
import { useNavigate } from 'react-router-dom';

const API_PORT = import.meta.env.VITE_API_PORT;
const API_URL = API_PORT ? `${import.meta.env.VITE_API_URL}:${API_PORT}` : import.meta.env.VITE_API_URL;

function PantryUserMenu({ user }: { user: User | null }): React.ReactNode {
    const [open, setOpen] = React.useState(false);
    const ref = React.useRef<HTMLDivElement>(null);
    const api = React.useContext(API.Context);
    const picture = user ? localStorage.getItem("user-picture") : null;

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

    async function revokeSession() {
        const sessionId = localStorage.getItem("session");
        if (sessionId) {
            try { await api!.revoke_session(sessionId); } catch {}
        }
        localStorage.removeItem("session");
        window.location.href = `${API_URL}/auth/google`;
    }

    return (
        <div className="pantry-user-menu" ref={ref}>
            <button className="pantry-avatar pantry-avatar-btn" onClick={() => setOpen(o => !o)} aria-label="Account menu">
                {user
                    ? (picture
                        ? <img src={picture} alt={user.email} className="pantry-avatar-img" referrerPolicy="no-referrer" />
                        : <span className="pantry-avatar-initials">{user.email[0].toUpperCase()}</span>)
                    : <span className="pantry-avatar-guest">?</span>
                }
            </button>
            {open && (
                <div className="pantry-menu-dropdown">
                    <div className="pantry-menu-email">{user ? user.email : "Visitor"}</div>
                    {user && <div className="pantry-menu-badge">{user.access_level}</div>}
                    <hr className="pantry-menu-divider" />
                    {user
                        ? <button className="pantry-menu-item" onClick={logOut}>Log Out</button>
                        : <button className="pantry-menu-item" onClick={revokeSession}>Revoke Session</button>
                    }
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
        <div className="report-modal-overlay" onClick={onClose}>
            <div className="report-modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Report an Issue</h3>
                <form onSubmit={handleSubmit}>
                    <textarea
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        placeholder="Describe the issue you encountered..."
                        rows={4}
                        maxLength={1000}
                        required
                        autoFocus
                    />
                    <div className="report-modal-buttons">
                        <button type="button" onClick={onClose}>Cancel</button>
                        <button type="submit" disabled={!message.trim()}>Submit Report</button>
                    </div>
                </form>
            </div>
        </div>
    );
}

type Panel = "products" | "brands" | "tags" | "settings";

function PanelContent({ panel, searchTerm, sortBy, sortDir, refreshKey }: { panel: Panel, searchTerm: string, sortBy: SortBy, sortDir: SortDir, refreshKey: number }): React.ReactNode {
    switch (panel) {
        case "products":  return <PantryView searchTerm={searchTerm} sortBy={sortBy} sortDir={sortDir} refreshKey={refreshKey} />;
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

    const [theme, cycleTheme] = useTheme();
    const [panel, _setPanel] = React.useState<Panel>("products");
    const [user, setUser] = React.useState<User | null>(null);
    const [sortBy, setSortBy] = React.useState<SortBy>('name');
    const [sortDir, setSortDir] = React.useState<SortDir>('asc');
    const [showCheckout, setShowCheckout] = React.useState(false);
    const [showReportModal, setShowReportModal] = React.useState(false);
    const [refreshKey, setRefreshKey] = React.useState(0);
    const navigate = useNavigate();
    const api = React.useContext(API.Context);

    const toggleSort = (field: SortBy) => {
        if (sortBy === field) {
            setSortDir(d => d === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortDir('asc');
        }
    };

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
            <div id="container" className="pantry-page">
                <div id="header">
                    <div id="title">
                        <img 
                            src={logo}
                            alt="Pantry Logo"
                            className="header-logo"
                        />
                        <span>Pirate Pantry</span>
                    </div>
                    <div id="header-center">
                        <div className="search-row">
                            <input // search bar
                                type="text"
                                placeholder="Search… or try id:110, name:, brand:, qty>N, qty<N"
                                value={searchTerm}
                                onChange={(e)=> setSearchTerm(e.target.value)}
                            />
                            <SortDropdown sortBy={sortBy} sortDir={sortDir} onToggle={toggleSort} />
                        </div>
                    </div>
                    <div id="header-top-right">
                        <div className="cart-group">
                            <div className="cart-icon">
                                🛒
                                <span className="cart-badge">{getCartCount()}</span>
                                <span className="cart-label">items in cart</span>
                            </div>
                            <button className="cart-clear-btn" onClick={() => clearCart()}>Clear Cart</button>
                            <button className="cart-checkout-btn" onClick={() => setShowCheckout(true)}>Checkout ⇒</button>
                        </div>
                    </div>
                    {user && <span className="header-separator" />}
                    <div className="nav-group">
                        {user && (
                            <button className="header-button" onClick={() => navigate("/workpanel")}>To Workpanel ➜</button>
                        )}
                        <span className="header-separator" />
                        <PantryUserMenu user={user} />
                    </div>
                </div>
                <div id="body">
                    <PanelContent panel={panel} searchTerm={searchTerm} sortBy={sortBy} sortDir={sortDir} refreshKey={refreshKey} />
                </div>
                <div id="footer">
                    <div id="footer-left">
                        <button
                            id="theme-toggle"
                            onClick={cycleTheme}
                            data-active={theme !== "auto" ? "" : undefined}
                        >
                            <span className="theme-icon">{THEME_ICONS[theme]}</span>
                            <span className="theme-name">{" "}{THEME_NAMES[theme]}</span>
                        </button>
                        {!user && (
                            <span id="anon-note">
                                🔒 Pantry is anonymous — checkouts are not tied to your identity.
                            </span>
                        )}
                    </div>
                    <div id="pagination-slot"></div>
                    <div id="footer-right">
                        <button className="report-issue-btn" onClick={() => setShowReportModal(true)}>Report Issue</button>
                    </div>
                </div>
            </div>
            {showCheckout && <CheckoutPanel onClose={() => setShowCheckout(false)} onSuccess={() => setRefreshKey(k => k + 1)} />}
            <ReportModal
                isOpen={showReportModal}
                onClose={() => setShowReportModal(false)}
                onSubmit={handleReportSubmit}
            />
        </Titled>
    );

};

