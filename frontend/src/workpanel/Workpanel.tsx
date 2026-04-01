import ProtectedPage from "../auth/ProtectedPage";
import Titled from "../misc/Titled";
import ProductView from "./ProductView";
import './Workpanel.css'

export default function Workpanel(): React.ReactNode {
    return (
        <ProtectedPage required_access_level="trusted">
            <Titled title="Pirate Pantry - Workpanel">
                <div id="container">
                    <div id="header">
                        <div id="title">Pirate Pantry Workpanel</div>
                        <div id="header-top-right">
                            <button id="user-view" className="header-button">User View</button>
                            <button id="log-out" className="header-button">Log Out</button> 
                        </div>
                    </div>
                    <div id="body">
                        <div id="body-left">
                            <button id="admin-panel" className="body-left-button">Admin Panel</button>
                            <button id="settings" className="body-left-button">Settings</button>
                        </div>
                        <ProductView />
                    </div>
                </div>
            </Titled>
        </ProtectedPage>
    );
}
