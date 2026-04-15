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
    const [showDialog, setShowDialog] = useState(false);

    const parsedTags = Array.from(
        new Set(
            tags    
                .split(",")
                .map((t: string) => t.trim())
                .filter(Boolean)  
        )
    );

    const handleYes = () => {
            setId("");
            setItemName("");
            setQuantity("");
            setBrand("");
            setTags("");
            setShowDialog(false);
    }

    const handleNo = () => {
        navigate("/workpanel", {state: {refresh: true}});
    };
    

    const handleSubmit = async () => {
        try{
            const newItem = {
                id: id,
                name: itemName,
                quantity: Number(quantity),
                brand,
                tags: parsedTags
            };

        console.log("New Item: ", newItem);

        const token = localStorage.getItem("session");

        const response = await fetch("http://localhost:5000/products", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization" : token || ""
                },
                body: JSON.stringify([newItem])
        });

        if(!response.ok){
            const err = await response.json();
            console.error("Backend error: ", err);
            throw new Error("Failed to add item");
        }

        await response.json();
         // try{
        //     console.log("Token being sent: ", localStorage.getItem("session"));
        //     const token = localStorage.getItem("session");
        //     const response = await fetch("http://localhost:5000/products", {
        //         method: "POST",
        //         credentials: "include",
        //         headers: { 
        //             "Content-Type": "application/json",
        //             "Authorizatoin" : token || ""
        //         },
        //         body: JSON.stringify({
        //             id: Number(id),
        //             name: itemName,
        //             quantity: Number(quantity),
        //             brand,
        //             tags: tags.split(",").map(tag => tag.trim())
        //         }),
        //     });
   

        //     if(!response.ok){
        //         throw new Error("Failed to add item");
        //     }    
        //     const data = await response.json();
        //     console.log("Saved", data);

            setId("");
            setItemName("");
            setQuantity("");
            setBrand("");
            setTags("");

            setShowDialog(true);
            // navigate("/workpanel", {state: {refresh: true}});

        } catch (error){
            console.error(error);
        }
    };

    return (
        <>
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
                        <button
                            className="done-button"
                            onClick={() => navigate("/workpanel")}
                        > Back</button>    
                    </div>
                </div>
            </div>

            {showDialog && (
                <div className="dialog-overlay">
                    <div className="dialog-box">
                        <p> Add another item?</p>
                        <div className="dialog-buttons">
                            <button onClick={handleYes}>Yes</button>
                            <button onClick={handleNo}>No</button>                
                        </div>
                    </div>
                </div>
            )}
        </>    
    );
};    
export default AddItem;