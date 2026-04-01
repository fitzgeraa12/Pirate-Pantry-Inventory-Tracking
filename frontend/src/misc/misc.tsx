import React from "react";

export type Optional<T> = T | null | undefined;

export function Spinner(): React.ReactNode {
    const delay = `-${Date.now() % 750}ms`;
    return <div className="spinner" style={{ animationDelay: delay }} />;
}
