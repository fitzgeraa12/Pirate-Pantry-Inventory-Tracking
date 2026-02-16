import './css_defaults/normalize.css'
import './css_defaults/skeleton.css'
import './App.css'
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import StudentFacing from './student/StudentFacing';
import WorkerFacing from './worker/WorkerFacing';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<StudentFacing />} />
        <Route path="/workpanel" element={<WorkerFacing />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
