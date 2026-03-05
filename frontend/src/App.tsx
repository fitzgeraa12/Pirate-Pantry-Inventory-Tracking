import './css_defaults/normalize.css'
import './css_defaults/skeleton.css'
import './App.css'
import { Navigate, Route, Routes } from 'react-router-dom';
import StudentFacing from './student/StudentFacing';
import WorkerFacing from './worker/WorkerFacing';
import AdminFacing from './admin/AdminFacing';
import ProtectedRoute from './misc/ProtectedRoute';

// https://www.kindacode.com/article/ways-to-set-page-title-dynamically-in-react
function App() {
  return (
    <Routes>
      <Route path="/" element={<StudentFacing />} />
      <Route path="/workpanel" element={
        <ProtectedRoute required_perms={["Trusted", "Admin"]}>
          <WorkerFacing />
        </ProtectedRoute>
      } />
      <Route path="adminpanel" element={
        <ProtectedRoute required_perms={["Admin"]}>
          <AdminFacing />
        </ProtectedRoute>
      } />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}

export default App;
