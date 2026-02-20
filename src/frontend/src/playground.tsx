import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import 'bootstrap/dist/css/bootstrap.css';
import Counter from './components/counter';

const element = <h1>Hello World</h1>;
ReactDOM.render(element, document.getElementById("root"));
registerServiceWorker();
