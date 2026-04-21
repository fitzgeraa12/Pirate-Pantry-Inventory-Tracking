import React from "react";

export type Optional<T> = T | null | undefined;

export class Option<T> {
    private value: T | null;

    private constructor(value: T | null) {
        this.value = value;
    }

    static some<U>(value: U): Option<U> {
        return new Option(value);
    }

    static none<U>(): Option<U> {
        return new Option<U>(null);
    }

    is_none(): boolean {
        return this.value === null;
    }

    is_some(): boolean {
        return this.value !== null;
    }

    unwrap(): T {
        if (this.value === null) {
            throw new Error("Called unwrap on a None value");
        }
        return this.value;
    }

    into_inner(): T | null {
        return this.value;
    }

    expect(msg: string): T {
        if (this.value === null) {
            throw new Error(msg);
        }
        return this.value;
    }
}

export function Spinner({ className }: { className?: string } = {}): React.ReactNode {
    const delay = `-${Date.now() % 750}ms`;
    return <div className={className ? `spinner ${className}` : "spinner"} style={{ animationDelay: delay }} />;
}
