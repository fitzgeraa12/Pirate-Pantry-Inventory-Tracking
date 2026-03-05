import { createContext } from "react";
import type { APIInterface } from "./API";

// https://react.dev/reference/react/createContext
export const APIContext = createContext<APIInterface | null>(null);
