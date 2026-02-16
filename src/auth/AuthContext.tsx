import { createContext } from "react";

// https://react.dev/reference/react/createContext
export const AuthContext = createContext<string | null>(null);
