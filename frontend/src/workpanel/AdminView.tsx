import React from "react";
import { API, type User, type Session, type AccessLevel } from "../API";
import { Spinner } from "../misc/misc";
import "./AdminView.css";

function fmt_date(ts: number): string {
    return new Date(ts * 1000).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function UsersSection({ api }: { api: API.Type }): React.ReactNode {
    const [users, setUsers] = React.useState<User[] | null>(null);
    const [saving, setSaving] = React.useState<Record<string, boolean>>({});

    React.useEffect(() => {
        api.get_users().then(setUsers);
    }, []);

    async function handleAccessChange(id: string, level: AccessLevel) {
        setSaving(s => ({ ...s, [id]: true }));
        try {
            const updated = await api.update_user(id, { access_level: level });
            setUsers(prev => prev?.map(u => u.id === id ? updated : u) ?? prev);
        } finally {
            setSaving(s => ({ ...s, [id]: false }));
        }
    }

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
                                    <select
                                        className="admin-select"
                                        value={user.access_level}
                                        disabled={saving[user.id]}
                                        onChange={e => handleAccessChange(user.id, e.target.value as AccessLevel)}
                                    >
                                        <option value="trusted">Trusted</option>
                                        <option value="admin">Admin</option>
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </section>
    );
}

function AddUserSection({ api, onAdded }: { api: API.Type; onAdded: () => void }): React.ReactNode {
    const [id, setId] = React.useState("");
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
            await api.add_user(id.trim(), email.trim(), level);
            setId("");
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
                    <label className="admin-form-label">Google Sub ID</label>
                    <input className="admin-form-input" value={id} onChange={e => setId(e.target.value)} placeholder="Google account sub…" />
                </div>
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
                        disabled={!id.trim() || !email.trim() || loading}
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

export default function AdminView(): React.ReactNode {
    const api = React.useContext(API.Context)!;
    const [usersKey, setUsersKey] = React.useState(0);

    return (
        <div className="admin-view">
            <UsersSection api={api} key={usersKey} />
            <AddUserSection api={api} onAdded={() => setUsersKey(k => k + 1)} />
            <SessionsSection api={api} />
        </div>
    );
}
