import BrandField from "./add_item/BrandField";
import IdField from "./add_item/IdField";
import NameField from "./add_item/NameField";
import QuantityField from "./add_item/QuantityField";
import TagsField from "./add_item/TagsField";

function App() {
    return (
        <div id="add-item-container">
            <div id="add-item-title">Add Item</div>
            <div id="add-item-body">
                <ol id="add-item-fields">
                    <IdField as="li" id="add-item-id-field"></IdField>
                    <NameField as="li" id="add-item-name-field"></NameField>
                    <BrandField as="li" id="add-item-brand-field"></BrandField>
                    <TagsField as="li" id="add-item-tags-field"></TagsField>
                    <QuantityField as="li" id="add-item-quantity-field"></QuantityField>
                </ol>
                <div id="add-item-buttons">
                    TODO: Buttons
                    {/* add-item-scan-barcode-button */}
                    {/* add-item-existing-product-button */}
                    {/* add-item-add-button */}
                </div>
            </div>
        </div>
    );
}

export default App;
