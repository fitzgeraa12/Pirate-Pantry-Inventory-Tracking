import React from "react";
import { API } from "../API";
import { Spinner } from "../misc/misc";
import "./SettingsView.css";

export default function SettingsView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [loginTimeout, setLoginTimeout] = React.useState("");
    const [pageSize, setPageSize] = React.useState(localStorage.getItem("table-page-size") ?? "20");
    const [loading, setLoading] = React.useState(true);
    const [saving, setSaving] = React.useState(false);
    const [saved, setSaved] = React.useState(false);

    React.useEffect(() => {
        api!.get_settings().then(s => {
            setLoginTimeout(s.login_timeout_days ?? "30");
            setLoading(false);
        });
    }, []);

    async function handleSave() {
        setSaving(true);
        setSaved(false);
        await api!.update_settings({ login_timeout_days: parseInt(loginTimeout) || 30 });
        localStorage.setItem("table-page-size", String(parseInt(pageSize) || 20));
        setSaving(false);
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    }

    if (loading) return <div id="placeholder-panel"><Spinner /></div>;

    return (
        <div className="settings-view">
            <div className="settings-card">
                <h2 className="settings-heading">Settings</h2>

                <div className="settings-group">
                    <label className="settings-label">Login Timeout (days)</label>
                    <p className="settings-description">How long a session lasts before requiring re-authentication.</p>
                    <input
                        className="settings-input"
                        type="number"
                        min="1"
                        max="365"
                        value={loginTimeout}
                        onChange={e => setLoginTimeout(e.target.value)}
                    />
                </div>

                <div className="settings-group">
                    <label className="settings-label">Table Page Size</label>
                    <p className="settings-description">Number of rows per page in data tables.</p>
                    <input
                        className="settings-input"
                        type="number"
                        min="5"
                        max="200"
                        value={pageSize}
                        onChange={e => setPageSize(e.target.value)}
                    />
                </div>

                <div className="settings-footer">
                    <button
                        className="settings-save-button"
                        onClick={handleSave}
                        disabled={saving}
                    >
                        {saving ? "Saving…" : saved ? "Saved ✓" : "Save"}
                    </button>
                </div>
            </div>
        </div>
    );
}
