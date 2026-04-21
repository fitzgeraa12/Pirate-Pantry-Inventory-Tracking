import { createContext } from "react";
import type { APIInterface } from "./API";
import { Optional } from "../misc/misc";

// https://react.dev/reference/react/createContext
export const APIContext = createContext<Option<APIInterface>>(Option.none());
