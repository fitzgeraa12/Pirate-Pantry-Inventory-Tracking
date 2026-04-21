import { Option } from '../misc/misc';
import { createContext } from "react";

// https://react.dev/reference/react/createContext
export interface AuthContextType{
    token: Option<string>;
    logout: () => void;
}
export const AuthContext = createContext<Option<AuthContextType>>(Option.none());
