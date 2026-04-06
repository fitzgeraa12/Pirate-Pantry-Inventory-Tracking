import React from "react";
import { Navigate } from "react-router-dom";
import { API } from "../API";
import { Spinner } from "./misc";

export default function HomeRedirect(): React.ReactNode {
  const [destination, setDestination] = React.useState<string | null>(null);
  const api = React.useContext(API.Context)!;

  React.useEffect(() => {
    api.get_user().then(user => {
      setDestination(user ? '/workpanel' : '/pantry');
    });
  }, []);

  if (!destination) return (
    <div className="page-loading">
        <div className="page-loading-title">Pirate Pantry</div>
        <Spinner />
    </div>
  );
  return <Navigate to={destination} />;
};