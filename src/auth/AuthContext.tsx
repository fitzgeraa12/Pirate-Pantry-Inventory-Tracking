import { createContext } from "react";

// https://react.dev/reference/react/createContext
interface AuthContextType{
    token: string;
    logout: () => void;
}
export const AuthContext = createContext<string | null>(null);
