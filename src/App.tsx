import './css_defaults/normalize.css'
import './css_defaults/skeleton.css'
import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom';
import StudentFacing from './student/StudentFacing';
import WorkerFacing from './worker/WorkerFacing';
import { useContext, useEffect, useState } from 'react';
import type { Perms } from './api/API';
import { AuthContext } from './auth/AuthContext';
import { APIContext } from './api/APIContext';
import Unauthorized from './misc/Unauthorized';

// https://www.kindacode.com/article/ways-to-set-page-title-dynamically-in-react
function App() {
  const auth = useContext(AuthContext);
  const api = useContext(APIContext);
  const [perms, set_perms] = useState<Perms | null>(null);

  // Once auth is acquired, acquire perms
  useEffect(() => {
    if (!auth) return;
    
    api!.cache_auth().then((cache_res) => {
      if (!cache_res) console.error("Failed to cache auth token");

      api!.get_perms().then((perms) => {
        set_perms(perms);
      }).catch(console.error);
    }).catch(console.error);
  }, [auth])

  return (
    <Routes>
      <Route path="/" element={<StudentFacing />} />
      <Route path="/workpanel" element={
        perms === "User" ? <Unauthorized /> : <WorkerFacing />
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
