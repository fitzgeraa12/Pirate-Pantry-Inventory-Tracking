import './css_defaults/normalize.css'
import './css_defaults/skeleton.css'
import './App.css'
import { Route, Routes } from 'react-router-dom';
import Workpanel from './workpanel/Workpanel';
import HomeRedirect from './misc/HomeRedirect';
import _404_ from './misc/404';
import Checkout from './checkout/Checkout';
import React from 'react';
import { API } from './API';

// https://www.kindacode.com/article/ways-to-set-page-title-dynamically-in-react
function App() {
  const api = React.useContext(API.Context);

  React.useEffect(() => {
    api!.whoami().then(google_sub => {
      console.log(`USER ID: ${google_sub}`);
    })
  }, []);

  return (
    <Routes>
      <Route path="/" element={<HomeRedirect />} />
      <Route path="/workpanel" element={<Workpanel />} />
      <Route path="/checkout" element={<Checkout />} />
      <Route path="*" element={<_404_></_404_>} />
    </Routes>
  );
}

export default App;
