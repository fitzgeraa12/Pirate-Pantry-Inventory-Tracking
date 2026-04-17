import React from "react";
import { SORT_LABELS, type SortBy, type SortDir } from "./searchParser";
import "./SortDropdown.css";

export default function SortDropdown({ sortBy, sortDir, onToggle }: {
    sortBy: SortBy;
    sortDir: SortDir;
    onToggle: (field: SortBy) => void;
}) {
    const [open, setOpen] = React.useState(false);
    const ref = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
        function onClickOutside(e: MouseEvent) {
            if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
        }
        document.addEventListener("mousedown", onClickOutside);
        return () => document.removeEventListener("mousedown", onClickOutside);
    }, []);

    return (
        <div className="sort-dropdown" ref={ref}>
            <button
                className="sort-dropdown-toggle"
                onClick={() => setOpen(o => !o)}
                aria-label="Sort options"
            >
                {sortBy === 'name' ? '' : SORT_LABELS[sortBy] + ' '}
                {sortDir === 'asc' ? '▲' : '▼'}
            </button>
            {open && (
                <div className="sort-dropdown-menu">
                    {(Object.keys(SORT_LABELS) as SortBy[]).map(field => (
                        <button
                            key={field}
                            className="sort-dropdown-item"
                            data-active={sortBy === field ? "" : undefined}
                            onClick={() => { onToggle(field); }}
                        >
                            {SORT_LABELS[field]}
                            {sortBy === field ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
