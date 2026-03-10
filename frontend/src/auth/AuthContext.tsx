import { createContext } from "react";

// https://react.dev/reference/react/createContext
export interface AuthContextType{
    token: string;
    logout: () => void;
}
export const AuthContext = createContext<AuthContextType | null>(null);
