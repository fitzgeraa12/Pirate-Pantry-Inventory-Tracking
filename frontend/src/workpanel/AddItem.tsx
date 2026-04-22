import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import "./AddItem.css";
import { API, type Product } from "../API";
import { Spinner } from "../misc/misc";


const AddItem = ({ editingProduct, onBack }: { editingProduct?: Product | null; onBack: () => void }) => {

    const [id, setId] = useState("");
    const [itemName, setItemName] = useState("");
    const [quantity, setQuantity] = useState("");
    const [brand, setBrand] = useState("");
    const [tags, setTags] = useState("");

    const [brands, setBrands] = useState<string[]>([]);
    const [allTags, setAllTags] = useState<string[]>([]);

    const isEditing = !!editingProduct;
    const api = React.useContext(API.Context);

    useEffect(() => {
        const loadOptions = async () => {
            try {
                const [brandsData, tagsData] = await Promise.all([
                    api!.get_all_brands(),
                    api!.get_all_tags()
                ]);
                setBrands(brandsData);
                setAllTags(tagsData);
            } catch (error) {
                console.error("Failed to load brands and tags:", error);
            }
        };
        loadOptions();
    }, [api]);

    useEffect(() => {
       if(editingProduct){
            setId(editingProduct.id?.toString() || "");
            setItemName(editingProduct.name || "");
            setQuantity(editingProduct.quantity?.toString() || "");
            setBrand(editingProduct.brand || "");
            setTags(editingProduct.tags ? editingProduct.tags.join(", ") : "");
        }
    }, [editingProduct]);

    const [loading, setLoading] = useState(false);

    const parsedTags = Array.from(
        new Set(
            tags
                .split(",")
                .map((t: string) => t.trim())
                .filter(Boolean)
        )
    );

    const handleSubmit = async () => {
        setLoading(true);
        try{
            const newItem = {
                id: id,
                name: itemName,
                quantity: Number(quantity),
                brand: brand || null,
                tags: parsedTags.length > 0 ? parsedTags : undefined
            };

            const idChanged = isEditing && editingProduct!.id !== id;
            if (idChanged) { // Delete old, then create new with new ID 
                await api!.delete_products([editingProduct!.id]); 
            }
            const responseData = await api!.add_products([newItem]);
            console.log("Response from server: ", responseData);

            onBack();

        } catch (error){
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return ReactDOM.createPortal(
        <div className="add-item-overlay" onMouseDown={(e) => { if (!loading && e.target === e.currentTarget) onBack(); }}>
            <div className="add-item-modal">
                <div className="add-item-modal-header">
                    <h3 className="add-item-modal-title">{isEditing ? "Edit Item" : "Add Item"}</h3>
                    <button className="add-item-close" onClick={onBack} disabled={loading} aria-label="Close">✕</button>
                </div>
                <div className="add-item-form">
                    <input
                        className="add-item-input"
                        type="text"
                        inputMode="numeric"
                        placeholder="Id"
                        value={id}
                        onChange={(e) => setId(e.target.value.replace(/\D/g, ''))}
                        disabled={loading}
                    />
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Name"
                        value={itemName}
                        onChange={(e) => setItemName(e.target.value.replace(/,/g, ''))}
                        disabled={loading}
                    />
                    <div className="quantity-counter">
                        <button
                            type="button"
                            className="quantity-button"
                            onClick={() => setQuantity(prev => Math.max(0, parseInt(prev || "0") - 1).toString())}
                        >-</button>
                        <input
                            className="quantity-input"
                            type="number"
                            min="0"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value)}
                            placeholder="0"
                        />
                        <button
                            type="button"
                            className="quantity-button"
                            onClick={() => setQuantity(prev => (parseInt(prev || "0") + 1).toString())}
                        >+</button>
                    </div>
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Brand"
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                        list="brands"
                    />
                    <datalist id="brands">
                        {brands.map(b => <option key={b} value={b} />)}
                    </datalist>
                    <input
                        className="add-item-input"
                        type="text"
                        placeholder="Tags"
                        value={tags}
                        onChange={(e) => setTags(e.target.value)}
                        list="tags"
                    />
                    <datalist id="tags">
                        {allTags.map(t => <option key={t} value={t} />)}
                    </datalist>
                    <div className="add-item-actions">
                        <button className="add-item-btn add-item-btn--primary" onClick={handleSubmit} disabled={loading}>
                            {loading ? <Spinner className="spinner--sm" /> : (isEditing ? "Save" : "Add")}
                        </button>
                        <button className="add-item-btn add-item-btn--secondary" onClick={onBack} disabled={loading}>Cancel</button>
                    </div>
                </div>
            </div>
        </div>,
        document.body
    );
};
export default AddItem;
