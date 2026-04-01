import React from "react";
import TableView from "./TableView";
import type { Optional } from "../misc/misc";
import { API, type User } from "../API";

export default function UserView(): React.ReactNode {
    const api = React.useContext(API.Context);
    const [users, setUsers] = React.useState<Optional<Array<User>>>(null);
    const pageSize = parseInt(localStorage.getItem("table-page-size") ?? "20") || 20;

    React.useEffect(() => {
        api!.get_users().then(setUsers);
    }, []);

    return (
        <TableView data={users} pageSize={pageSize} column_meta={{
            meta: {
                id:           { header: "ID" },
                email:        { header: "Email" },
                access_level: { header: "Access Level" },
            },
            order: ["id", "email", "access_level"],
        }} />
    );
}
