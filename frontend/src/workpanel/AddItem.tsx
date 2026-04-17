import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
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

            const idChanged = isEditing && editingProduct!.id !== id;
            if (idChanged) {
                // Delete old, then create new with new ID
                await api!.delete_products([editingProduct!.id]);
            }
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

    return ReactDOM.createPortal(
        <div className="add-item-overlay" onMouseDown={(e) => { if (e.target === e.currentTarget) onBack(); }}>
            <div className="add-item-modal">
                <div className="add-item-modal-header">
                    <h3 className="add-item-modal-title">{isEditing ? "Edit Item" : "Add Item"}</h3>
                    <button className="add-item-close" onClick={onBack} aria-label="Close">✕</button>
                </div>
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
                        onChange={(e) => setItemName(e.target.value.replace(/,/g, ''))}
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
                        onChange={(e) => setBrand(e.target.value.replace(/,/g, ''))}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Tags (comma separated)"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                    />
                    <div className="add-item-actions">
                        <button className="add-item-btn add-item-btn--primary" onClick={handleSubmit}>
                            {isEditing ? "Save" : "Add"}
                        </button>
                        <button className="add-item-btn add-item-btn--secondary" onClick={onBack}>Cancel</button>
                    </div>
                </div>
            </div>

            {showDialog && (
                <div className="add-item-dialog">
                    <div className="add-item-dialog-box">
                        <p>Add another item?</p>
                        <div className="add-item-dialog-buttons">
                            <button className="add-item-btn add-item-btn--primary" onClick={handleYes}>Yes</button>
                            <button className="add-item-btn add-item-btn--secondary" onClick={handleNo}>No</button>
                        </div>
                    </div>
                </div>
            )}
        </div>,
        document.body
    );
};    
export default AddItem;