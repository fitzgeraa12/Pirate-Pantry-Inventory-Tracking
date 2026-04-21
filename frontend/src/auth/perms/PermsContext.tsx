import { Option } from '../../misc/misc';
import { createContext } from "react";
import type { PermsInterface } from "./Perms";
import type { Optional } from "../../misc/misc";

export const PermsContext = createContext<Option<PermsInterface>>(Option.none());
