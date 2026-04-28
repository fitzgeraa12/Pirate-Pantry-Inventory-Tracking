import React from "react";
import { API, type User, type Session, type AccessLevel } from "../API";
import { Spinner } from "../misc/misc";
import { createPortal } from "react-dom";  
import "./AdminView.css";

function fmt_date(ts: number): string {
    return new Date(ts * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function UsersSection({ api }: { api: API.Type }): React.ReactNode {
    const [users, setUsers] = React.useState<User[] | null>(null);
    const [currentUser, setCurrentUser] = React.useState<User | null>(null);
    const [saving, setSaving] = React.useState<Record<string, boolean>>({});
    const [error, setError] = React.useState<string | null>(null);

    React.useEffect(() => {
        api.get_users().then(setUsers);
        api.get_user().then(user => setCurrentUser(user ?? null));
    }, []);

    async function handleAccessChange(id: string, level: AccessLevel) {
        setSaving(s => ({ ...s, [id]: true }));
        setError(null);
        try {
            const updated = await api.update_user(id, { access_level: level });
            setUsers(prev => prev?.map(u => u.id === id ? updated : u) ?? prev);
        } catch (e: any) {
            setError(e?.response?.data?.error ?? "Failed to update user");
        } finally {
            setSaving(s => ({ ...s, [id]: false }));
        }
    }

    const adminCount = users?.filter(user => user.access_level === "admin").length ?? 0;

    return (
        <section className="admin-section">
            <h2 className="admin-section-heading">Users</h2>
            {users === null ? (
                <div className="admin-loading"><Spinner /></div>
            ) : (
                <table className="admin-table">
                    <thead>
                        <tr><th>Email</th><th>ID</th><th>Access Level</th></tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>{user.email}</td>
                                <td className="admin-id-cell">{user.id.slice(0, 16)}…</td>
                                <td>
                                    {(() => {
                                        const isOnlyAdminSelf = currentUser?.id === user.id && user.access_level === "admin" && adminCount === 1;
                                        return (
                                    <select
                                        className="admin-select"
                                        value={user.access_level}
                                        disabled={saving[user.id] || isOnlyAdminSelf}
                                        onChange={e => handleAccessChange(user.id, e.target.value as AccessLevel)}
                                    >
                                        <option value="trusted">Trusted</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                        );
                                    })()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
            {error && <div className="admin-error">{error}</div>}
        </section>
    );
}

function AddUserSection({ api, onAdded }: { api: API.Type; onAdded: () => void }): React.ReactNode {
    const [email, setEmail] = React.useState("");
    const [level, setLevel] = React.useState<AccessLevel>("trusted");
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [success, setSuccess] = React.useState(false);

    async function handleAdd() {
        setLoading(true);
        setError(null);
        setSuccess(false);
        try {
            await api.add_user(email.trim(), level);
            setEmail("");
            setLevel("trusted");
            setSuccess(true);
            setTimeout(() => setSuccess(false), 2000);
            onAdded();
        } catch (e: any) {
            setError(e?.response?.data?.error ?? "Failed to add user");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="admin-section">
            <h2 className="admin-section-heading">Add User</h2>
            <div className="admin-form">
                <div className="admin-form-row">
                    <label className="admin-form-label">Email</label>
                    <input className="admin-form-input" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="user@southwestern.edu" />
                </div>
                <div className="admin-form-row">
                    <label className="admin-form-label">Access Level</label>
                    <select className="admin-select" value={level} onChange={e => setLevel(e.target.value as AccessLevel)}>
                        <option value="trusted">Trusted</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>
                <div className="admin-form-actions">
                    <button
                        className="admin-submit-button"
                        disabled={!email.trim() || loading}
                        onClick={handleAdd}
                    >
                        {loading ? "Adding…" : success ? "Added ✓" : "Add User"}
                    </button>
                    {error && <span className="admin-error">{error}</span>}
                </div>
            </div>
        </section>
    );
}

function SessionsSection({ api }: { api: API.Type }): React.ReactNode {
    const [sessions, setSessions] = React.useState<Session[] | null>(null);
    const [revoking, setRevoking] = React.useState<Record<string, boolean>>({});

    React.useEffect(() => {
        api.get_sessions().then(setSessions);
    }, []);

    async function handleRevoke(id: string) {
        setRevoking(r => ({ ...r, [id]: true }));
        try {
            await api.revoke_session(id);
            setSessions(prev => prev?.filter(s => s.id !== id) ?? prev);
        } finally {
            setRevoking(r => ({ ...r, [id]: false }));
        }
    }

    return (
        <section className="admin-section">
            <h2 className="admin-section-heading">Active Sessions</h2>
            {sessions === null ? (
                <div className="admin-loading"><Spinner /></div>
            ) : (
                <table className="admin-table">
                    <thead>
                        <tr><th>User</th><th>Created</th><th>Expires</th><th></th></tr>
                    </thead>
                    <tbody>
                        {sessions.map(s => (
                            <tr key={s.id} className={s.is_current ? "admin-current-row" : undefined}>
                                <td>
                                    {s.user_email ?? <em>Visitor</em>}
                                    {s.is_current && <span className="admin-current-badge">you</span>}
                                </td>
                                <td>{fmt_date(s.created_at)}</td>
                                <td>{fmt_date(s.expires_at)}</td>
                                <td>
                                    <button
                                        className="admin-revoke-button"
                                        disabled={s.is_current || revoking[s.id]}
                                        onClick={() => handleRevoke(s.id)}
                                    >Revoke</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </section>
    );
}

function BackupSection({ api }: { api: API.Type }): React.ReactNode {
    const [loading, setLoading] = React.useState(false);
    const [message, setMessage] = React.useState<string | null>(null);
    const [error, setError] = React.useState<string | null>(null);
    const [open, setOpen] = React.useState(false);

    async function handleRevert() {
        setLoading(true);
        setMessage(null);
        setError(null);

        try {
            const res = await api.revert_backup();
            setMessage(res.message || "Inventory reverted successfully");
            setOpen(false);
            setTimeout(() => window.location.reload(), 1000);
        } catch (e: any) {
            setError(e?.response?.data?.error ?? "Failed to revert inventory");
        } finally {
            setLoading(false);
        }
    }

    return (
        <section className="admin-section admin-danger-zone">
            <h2 className="admin-section-heading">Danger Zone</h2>

            <div className="admin-form">
                <p className="admin-warning-text">
                    Reverting will overwrite all current products with the last saved backup.
                </p>

                <button
                    className="admin-danger-button"
                    onClick={() => setOpen(true)}
                    disabled={loading}
                >
                    {loading ? "Reverting…" : "Revert to Last Backup"}
                </button>

                {message && <div className="admin-success">{message}</div>}
                {error && <div className="admin-error">{error}</div>}
            </div>

            <RevertBackupModal
                open={open}
                loading={loading}
                onCancel={() => setOpen(false)}
                onConfirm={handleRevert}
            />
        </section>
    );
}

function RevertBackupModal({
    open,
    loading,
    onConfirm,
    onCancel,
}: {
    open: boolean;
    loading: boolean;
    onConfirm: () => void;
    onCancel: () => void;
}) {
    if (!open) return null;

    return createPortal(
        <div
            className="modal-overlay"
            onMouseDown={(e) => {
                if (!loading && e.target === e.currentTarget) onCancel();
            }}
        >
            <div className="modal-container">
                <div className="modal-header">
                    <h3 className="modal-title">Revert Database</h3>
                    <button
                        className="modal-close"
                        onClick={onCancel}
                        disabled={loading}
                        aria-label="Close"
                    >
                        ✕
                    </button>
                </div>

                <div className="modal-body">
                    <p>
                        This will replace all current products with the last saved backup.
                        This action cannot be undone.
                    </p>

                    <div className="modal-actions">
                        <button
                            className="modal-btn modal-btn--primary"
                            onClick={onConfirm}
                            disabled={loading}
                        >
                            {loading ? "Reverting..." : "Revert"}
                        </button>

                        <button
                            className="modal-btn modal-btn--secondary"
                            onClick={onCancel}
                            disabled={loading}
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
}

export default function AdminView(): React.ReactNode {
    const api = React.useContext(API.Context)!;
    const [usersKey, setUsersKey] = React.useState(0);

    return (
        <div className="admin-view">
            <UsersSection api={api} key={usersKey} />
            <AddUserSection api={api} onAdded={() => setUsersKey(k => k + 1)} />
            <SessionsSection api={api} />
            <BackupSection api={api} />
        </div>
    );
}
