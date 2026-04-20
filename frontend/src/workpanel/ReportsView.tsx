import React from "react";
import { API, type Report } from "../API";

export default function ReportsView(): React.ReactNode {
    const [reports, setReports] = React.useState<Report[]>([]);
    const [loading, setLoading] = React.useState(true);
    const api = React.useContext(API.Context);

    React.useEffect(() => {
        loadReports();
    }, []);

    function loadReports() {
        setLoading(true);
        api!.get_reports()
            .then(setReports)
            .catch(err => {
                console.error("Failed to load reports:", err);
                alert("Failed to load reports");
            })
            .finally(() => setLoading(false));
    }

    function handleResolve(reportId: string) {
        api!.resolve_report(reportId)
            .then(() => {
                setReports(reports.map(r =>
                    r.id === reportId ? { ...r, resolved: true } : r
                ));
            })
            .catch(err => {
                console.error("Failed to resolve report:", err);
                alert("Failed to resolve report");
            });
    }

    function formatDate(timestamp: number): string {
        return new Date(timestamp * 1000).toLocaleString();
    }

    if (loading) {
        return <div className="loading">Loading reports...</div>;
    }

    const unresolvedReports = reports.filter(r => !r.resolved);
    const resolvedReports = reports.filter(r => r.resolved);

    return (
        <div className="reports-view">
            <h2>Student Reports</h2>

            {unresolvedReports.length > 0 && (
                <div className="reports-section">
                    <h3>Unresolved Reports ({unresolvedReports.length})</h3>
                    <div className="reports-list">
                        {unresolvedReports.map(report => (
                            <div key={report.id} className="report-card unresolved">
                                <div className="report-header">
                                    <div className="report-user">{report.user_email}</div>
                                    <div className="report-date">{formatDate(report.created_at)}</div>
                                </div>
                                <div className="report-message">{report.message}</div>
                                <div className="report-actions">
                                    <button
                                        className="resolve-button"
                                        onClick={() => handleResolve(report.id)}
                                    >
                                        Mark as Resolved
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {resolvedReports.length > 0 && (
                <div className="reports-section">
                    <h3>Resolved Reports ({resolvedReports.length})</h3>
                    <div className="reports-list">
                        {resolvedReports.map(report => (
                            <div key={report.id} className="report-card resolved">
                                <div className="report-header">
                                    <div className="report-user">{report.user_email}</div>
                                    <div className="report-date">{formatDate(report.created_at)}</div>
                                </div>
                                <div className="report-message">{report.message}</div>
                                <div className="report-status">✓ Resolved</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {reports.length === 0 && (
                <div className="no-reports">No reports submitted yet.</div>
            )}
        </div>
    );
}