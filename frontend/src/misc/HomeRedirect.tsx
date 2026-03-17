import React from "react";
import { Navigate } from "react-router-dom";
import { API } from "../API";

export default function HomeRedirect(): React.ReactNode {
  const [destination, setDestination] = React.useState<string | null>(null);
  const api = React.useContext(API.Context)!;

  React.useEffect(() => {
    api.get_user().then(user => {
      setDestination(user ? '/workpanel' : '/checkout');
    });
  }, []);

  if (!destination) return <div>Loading...</div>;
  return <Navigate to={destination} />;
};