import React, { useState } from "react";
import ReactDOM from "react-dom";
import { API } from "../API";
import "./AddItem.css";

export default function ExportModal({ onClose }: { onClose: () => void }) {
    const api = React.useContext(API.Context);
    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    function toMMDDYYYY(dateStr: string): string {
        const [y, m, d] = dateStr.split("-");
        return `${m}-${d}-${y}`;
    }

    async function handleExport() {
        if (!start || !end) { setError("Both dates are required."); return; }
        setError("");
        setLoading(true);
        try {
            const blob = await api!.export_stats(toMMDDYYYY(start), toMMDDYYYY(end));
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `Pirate_Pantry_Stats_${toMMDDYYYY(start)}_to_${toMMDDYYYY(end)}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            URL.revokeObjectURL(url);
            onClose();
        } catch (e: any) {
            setError(e?.response?.data?.error || e?.message || "Export failed.");
        } finally {
            setLoading(false);
        }
    }

    return ReactDOM.createPortal(
        <div className="add-item-overlay" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}>
            <div className="add-item-modal">
                <div className="add-item-modal-header">
                    <h3 className="add-item-modal-title">Export Stats</h3>
                    <button className="add-item-close" onClick={onClose} aria-label="Close">✕</button>
                </div>
                <div className="add-item-form">
                    <label className="export-label">Start Date</label>
                    <input
                        className="add-item-input"
                        type="date"
                        value={start}
                        onChange={(e) => setStart(e.target.value)}
                    />
                    <label className="export-label">End Date</label>
                    <input
                        className="add-item-input"
                        type="date"
                        value={end}
                        onChange={(e) => setEnd(e.target.value)}
                    />
                    {error && <div className="export-error">{error}</div>}
                    <div className="add-item-actions">
                        <button
                            className="add-item-btn add-item-btn--primary"
                            onClick={handleExport}
                            disabled={loading}
                        >
                            {loading ? "Exporting…" : "Download PDF"}
                        </button>
                        <button className="add-item-btn add-item-btn--secondary" onClick={onClose}>Cancel</button>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
}
