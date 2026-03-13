import { createContext } from "react";
import { Option } from "../misc/misc";

// https://react.dev/reference/react/createContext
export interface AuthContextType{
    token: Option<string>;
    logout: () => void;
}
export const AuthContext = createContext<Option<AuthContextType>>(Option.none());
