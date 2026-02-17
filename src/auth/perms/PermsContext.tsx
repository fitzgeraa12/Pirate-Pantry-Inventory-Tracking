import { createContext } from "react";
import type { PermsInterface } from "./Perms";

export const PermsContext = createContext<PermsInterface | null>(null);
