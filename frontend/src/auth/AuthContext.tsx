import { Option } from '../misc/misc';
import { createContext } from "react";
import type { Optional } from "../misc/misc";

// https://react.dev/reference/react/createContext
export interface AuthContextType{
    token: Optional<string>;
    logout: () => void;
}
export const AuthContext = createContext<Option<AuthContextType>>(Option.none());
