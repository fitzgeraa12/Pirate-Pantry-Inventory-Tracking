import React from "react";
import ProtectedPage from "../auth/ProtectedPage";
import Titled from "../misc/Titled";
import ProductView from "./ProductView";
import BrandView from "./BrandView";
import TagView from "./TagsView";
import UserView from "./UserView";
import AdminView from "./AdminView";
import SettingsView from "./SettingsView";
import AddItem from "./AddItem";
import ReportsView from "./ReportsView";
import ExportModal from "./ExportModal";
import { useTheme } from "../misc/useTheme";
import { useNavigate, useSearchParams } from "react-router-dom";
import { API, type User, type Product } from "../API";
import './Workpanel.css'

const THEME_LABELS = { light: "☀  Light", dark: "🌙  Dark", auto: "⊙  System" };

type Panel = "products" | "brands" | "tags" | "users" | "admin" | "settings" | "addItem" | "reports";

const DEFAULT_PANEL: Panel = "products";

function is_panel(value: string | null): value is Panel {
    return value === "products" || value === "brands" || value === "tags" || value === "users" || value === "admin" || value === "settings" || value === "addItem" || value === "reports";
}

function can_access_panel(panel: Panel, user: User | null): boolean {
    if (panel === "users" || panel === "admin" || panel === "reports") return user?.access_level === "admin";
    return true;
}

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

export default function Workpanel(): React.ReactNode {
    const [searchParams, setSearchParams] = useSearchParams();
    const [theme, cycleTheme] = useTheme();
    const [panel, setPanel] = React.useState<Panel>(() => {
        const candidate = searchParams.get("panel");
        return is_panel(candidate) ? candidate : DEFAULT_PANEL;
    });
    const [user, setUser] = React.useState<User | null>(null);
    const [editingProduct, setEditingProduct] = React.useState<Product | null>(null);
    const [addItemOpen, setAddItemOpen] = React.useState(false);
    const [exportOpen, setExportOpen] = React.useState(false);
    const [sidebarOpen, setSidebarOpen] = React.useState(false);
    const navigate = useNavigate();
    const api = React.useContext(API.Context);

    function PanelContent({ panel }: { panel: Panel }): React.ReactNode {
        switch (panel) {
            case "products":  return <ProductView onEdit={(p) => { setEditingProduct(p); setAddItemOpen(true); }} />;
            case "brands":    return <BrandView />;
            case "tags":      return <TagView />;
            case "users":     return <UserView />;
            case "admin":     return <AdminView />;
            case "settings":  return <SettingsView />;
            case "addItem":   return <AddItem editingProduct={editingProduct} onBack={() => setPanel("products")} />;
            case "reports":   return <ReportsView />;
        }
    }

    React.useEffect(() => {
        api!.get_user().then(u => { if (u) setUser(u); });
    }, [api]);

    React.useEffect(() => {
        const candidate = searchParams.get("panel");
        if (!is_panel(candidate)) {
            if (panel !== DEFAULT_PANEL) setPanel(DEFAULT_PANEL);
            return;
        }
        if (candidate !== panel) setPanel(candidate);
    }, [searchParams]);

    React.useEffect(() => {
        const resolvedPanel = can_access_panel(panel, user) ? panel : DEFAULT_PANEL;
        if (resolvedPanel !== panel) {
            setPanel(resolvedPanel);
            return;
        }

        const currentInUrl = searchParams.get("panel");
        if (currentInUrl !== resolvedPanel) {
            const next = new URLSearchParams(searchParams);
            next.set("panel", resolvedPanel);
            setSearchParams(next, { replace: true });
        }
    }, [panel, user, searchParams, setSearchParams]);

    function setPanelAndUrl(next: Panel) {
        setPanel(next);
        setSidebarOpen(false);
        const params = new URLSearchParams(searchParams);
        params.set("panel", next);
        setSearchParams(params, { replace: true });
    }

    return (
        <ProtectedPage required_access_level="trusted">
            <Titled title="Pirate Pantry - Workpanel">
                <div id="container">
                    <div id="header">
                        <button className="sidebar-toggle" onClick={() => setSidebarOpen(o => !o)} aria-label="Toggle menu">
                            {sidebarOpen ? '✕' : '☰'}
                        </button>
                       <div id="title">
                            <img 
                                src="/workspaces/Pirate-Pantry-Inventory-Tracking/Pantry_logo.jpg"
                                alt="Pantry Logo"
                                className="header-logo"
                            />
                            <span>Workpanel</span>
                        </div>
                        <div id="header-toolbar"></div>
                        <div id="header-top-right">
                            <button id="user-view" className="header-button" onClick={() => navigate("/pantry")}>To Pantry ➜</button>
                            <span className="header-separator" />
                            {user && <UserMenu user={user} />}
                        </div>
                    </div>
                    <div id="body">
                        {sidebarOpen && <div className="sidebar-backdrop" onClick={() => setSidebarOpen(false)} />}
                        <div id="body-left" className={sidebarOpen ? '' : 'sidebar-collapsed'}>
                            <span className="body-left-section-label">Database</span>
                            <button className="body-left-button body-left-sub-button" onClick={() => setPanelAndUrl("products")} data-active={panel === "products" ? "" : undefined}>Products</button>
                            <button className="body-left-button body-left-sub-button" onClick={() => setPanelAndUrl("brands")}  data-active={panel === "brands"   ? "" : undefined}>Brands</button>
                            <button className="body-left-button body-left-sub-button" onClick={() => setPanelAndUrl("tags")}    data-active={panel === "tags"     ? "" : undefined}>Tags</button>
                            {user?.access_level === "admin" && (
                                <button className="body-left-button body-left-sub-button" onClick={() => setPanelAndUrl("users")} data-active={panel === "users" ? "" : undefined}>Users</button>
                            )}
                            <div className="body-left-spacer" />
                            <hr className="body-left-divider" />
                            <button className="body-left-button body-left-button-additem" onClick={ () => { setEditingProduct(null); setAddItemOpen(true); setSidebarOpen(false); }}> Add Item</button>
                            {user?.access_level === "admin" && (
                                <button className="body-left-button" onClick={() => { setExportOpen(true); setSidebarOpen(false); }}>Statistics</button>
                            )}
                            <button className="body-left-button" onClick={() => setPanelAndUrl("settings")} data-active={panel === "settings" ? "" : undefined}>Settings</button>
                            {user?.access_level === "admin" && (
                                <button className="body-left-button" onClick={() => setPanelAndUrl("admin")} data-active={panel === "admin" ? "" : undefined}>Admin Panel</button>
                            )}
                            {user?.access_level === "admin" && (
                                <button className="body-left-button" onClick={() => setPanelAndUrl("reports")} data-active={panel === "reports" ? "" : undefined}>Reports</button>
                            )}
                            <hr className="body-left-divider" />
                            <span className="body-left-section-label">Appearance</span>
                            <button className="body-left-button body-left-button--sm" onClick={cycleTheme} data-active={theme !== "auto" ? "" : undefined}>
                                Theme: {THEME_LABELS[theme]}
                            </button>
                        </div>
                        <PanelContent panel={panel} />
                    </div>
                    <button className="wp-add-btn" onClick={() => { setEditingProduct(null); setAddItemOpen(true); }} aria-label="Add Item">＋</button>
                    {addItemOpen && <AddItem editingProduct={editingProduct} onBack={() => setAddItemOpen(false)} />}
                    {exportOpen && <ExportModal onClose={() => setExportOpen(false)} />}
                </div>
            </Titled>
        </ProtectedPage>
    );
}
