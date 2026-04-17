import React from "react";

export type ThemePreference = "light" | "dark" | "auto";

const STORAGE_KEY = "theme-preference";

export function useTheme(): [ThemePreference, () => void] {
    const [theme, setTheme] = React.useState<ThemePreference>(() => {
        return (localStorage.getItem(STORAGE_KEY) as ThemePreference) ?? "auto";
    });

    React.useEffect(() => {
        const root = document.documentElement;
        if (theme === "auto") {
            root.removeAttribute("data-theme");
            localStorage.removeItem(STORAGE_KEY);
        } else {
            root.setAttribute("data-theme", theme);
            localStorage.setItem(STORAGE_KEY, theme);
        }
    }, [theme]);

    const cycle = React.useCallback(() => {
        setTheme(t => t === "auto" ? "light" : t === "light" ? "dark" : "auto");
    }, []);

    return [theme, cycle];
}
