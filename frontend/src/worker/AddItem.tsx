import { useState } from "react";
import "./AddItem.css";
import { useNavigate } from "react-router-dom";
import { useLocation } from "react-router-dom";

const AddItem = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const item = location.state || {};

    const [id, setId] = useState(item.id || "");
    const [itemName, setItemName] = useState(item.itemName || "");
    const [quantity, setQuantity] = useState(item.quantity || "");
    const [brand, setBrand] = useState(item.brand || "");
    const [tags, setTags] = useState(item.tags || "");
    

    const handleSubmit = () => {
        const newItem = {
            id, 
            itemName,
            quantity,
            brand,
            tags
        };

        console.log("New Item: ", newItem);
        //TODO backend 

        setId("");
        setItemName("");
        setQuantity("");
        setBrand("");
        setTags("");

        navigate("/workpanel");
    };

    return (
        <div className="add-item-page">
            <div className="add-item-card">
                <button className="placeholder-button"> Scan</button>
                <div className="add-item-form">
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Id"
                        value={id}
                        onChange={(e) => setId(e.target.value)}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Name"
                        value={itemName}
                        onChange={(e) => setItemName(e.target.value)}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Quantity"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Brand"
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Tags"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                    />    

                    <button
                        className="done-button"
                        onClick={handleSubmit}
                    >Done</button>
                </div>
            </div>
        </div>
    );
};    
export default AddItem;