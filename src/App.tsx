import './css_defaults/normalize.css'
import './css_defaults/skeleton.css'
import './App.css'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import StudentFacing from './student/StudentFacing';
import WorkerFacing from './worker/WorkerFacing';
import { useContext, useEffect, useState } from 'react';
import type { Perms } from './api/API';
import { AuthContext } from './auth/AuthContext';
import { APIContext } from './api/APIContext';

function App() {
  const auth = useContext(AuthContext);
  const api = useContext(APIContext);
  const [perms, set_perms] = useState<Perms | null>(null);
  const navigate_to = useNavigate();

  // Once auth is acquired, acquire perms
  useEffect(() => {
    if (!auth) return;
    
    api!.cache_auth().then((cache_res) => {
      if (!cache_res) console.error("Failed to cache auth token");

      api!.get_perms().then((perms) => {
        console.log(perms);
        set_perms(perms);

        switch (perms) {
          case "Trusted":
          case "Admin":
            navigate_to("/workpanel");
            break;
          default:
            navigate_to("/");
        }
      }).catch(console.error);
    }).catch(console.error);
  }, [auth])

  return (
    <Routes>
      <Route path="/" element={<StudentFacing />} />
      {(perms === "Trusted" || perms === "Admin") && (
          <Route path="/workpanel" element={<WorkerFacing />} />
      )}
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
