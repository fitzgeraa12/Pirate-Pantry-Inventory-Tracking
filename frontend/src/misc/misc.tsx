import React from "react";

export type Optional<T> = T | null | undefined;

export function Spinner({ className }: { className?: string } = {}): React.ReactNode {
    const delay = `-${Date.now() % 750}ms`;
    return <div className={className ? `spinner ${className}` : "spinner"} style={{ animationDelay: delay }} />;
}
