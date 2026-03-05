import './WorkerFacing.css'
import Titled from '../misc/Titled';
import { useCallback, type ReactElement } from 'react';
import ProductView from './views/ProductView';
import { useSearchParams } from 'react-router-dom';
import BrandView from './views/BrandView';
import TagsView from './views/TagsView';
import ErrorView from './views/ErrorView';

// https://tanstack.com/table/latest/docs/guide/tables
// https://tanstack.com/table/latest/docs/guide/column-defs
// https://stackoverflow.com/questions/76157947/border-radius-doesnt-round-the-borders-of-my-table-but-the-background-color
function WorkerFacing() {
    const [search_params, set_search_params] = useSearchParams();

    const decide_view = useCallback((): ReactElement => {
        let view: ReactElement;
        switch (search_params.get("view")) {
            case "brand":
                view = <BrandView />;
                break;
            case "tags":
                view = <TagsView />;
                break;
            case "product":
                view = <ProductView />;
                break;
            case null:
                set_search_params({ "view": "product" });
                view = <ProductView />;
                break;
            default:
                view = <ErrorView />;
        }

        return view;
    }, [search_params]);

    return (
        <Titled title="Workpanel">
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
                    {decide_view()}
                </div>
            </div>
        </Titled>
    );
}

export default WorkerFacing;
