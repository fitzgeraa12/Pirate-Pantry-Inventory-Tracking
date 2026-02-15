import { useCallback, useState } from 'react';
import './App.css';
import AddItem from './inventory/AddItem';

function App() {
    const [add_item_enabled, set_add_item_enabled] = useState(true);

    return (
        <>
            {add_item_enabled && <AddItem />}
        </>
    );
}

export default App;
