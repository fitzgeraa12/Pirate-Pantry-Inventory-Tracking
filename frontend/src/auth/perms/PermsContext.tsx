import { createContext } from "react";
import type { PermsInterface } from "./Perms";
import { Optional } from "../../misc/misc";

export const PermsContext = createContext<Option<PermsInterface>>(Option.none());
