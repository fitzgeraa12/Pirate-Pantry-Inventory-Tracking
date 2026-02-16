import { useEffect } from 'react';
import './WorkerFacing.css'

const WORKER_FACING_TITLE = "Pirate Pantry - Workpanel"

function WorkerFacing() {
    // Runs once at start
    useEffect(() => {
        document.title = WORKER_FACING_TITLE;
    }, [])

    return (
        <div id="container">
            
        </div>
    );
}

export default WorkerFacing;
