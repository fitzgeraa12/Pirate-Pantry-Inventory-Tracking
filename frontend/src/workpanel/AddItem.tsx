import React, { useState, useEffect } from "react";
import "./AddItem.css";
import { API, type Product } from "../API";


const AddItem = ({ editingProduct, onBack }: { editingProduct?: Product | null; onBack: () => void }) => {

    const [id, setId] = useState("");
    const [itemName, setItemName] = useState("");
    const [quantity, setQuantity] = useState("");
    const [brand, setBrand] = useState("");
    const [tags, setTags] = useState("");

    const isEditing = !!editingProduct;
    const api = React.useContext(API.Context);

    useEffect(() => {
       if(editingProduct){
            console.log("Loading product for edit:", editingProduct);
            setId(editingProduct.id?.toString() || "");
            setItemName(editingProduct.name || "");
            setQuantity(editingProduct.quantity?.toString() || "");
            setBrand(editingProduct.brand || "");
            setTags(editingProduct.tags ? editingProduct.tags.join(", ") : "");
            console.log("Brand set to:", editingProduct.brand);
            console.log("Tags set to:", editingProduct.tags ? editingProduct.tags.join(", ") : "");
        }
    }, [editingProduct]);

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
        onBack();
    };
    

    const handleSubmit = async () => {
        try{
            const newItem = {
                id: id,
                name: itemName,
                quantity: Number(quantity),
                brand: brand || null,
                tags: parsedTags.length > 0 ? parsedTags : undefined
            };

        console.log("Submitting item:", JSON.stringify([newItem], null, 2));

            const responseData = await api!.add_products([newItem]);
            console.log("Response from server: ", responseData);

            if (isEditing) {
                onBack();
            } else {
                setId("");
                setItemName("");
                setQuantity("");
                setBrand("");
                setTags("");
                setShowDialog(true);
            }

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
                            onClick={onBack}
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