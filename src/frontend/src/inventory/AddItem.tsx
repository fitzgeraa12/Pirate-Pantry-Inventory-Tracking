import { useEffect, useState } from "react";

// // https://www.webdevtutor.net/blog/typescript-check-if-number-is-an-integer
// type Id = number & { readonly _id: true };
// const ID_MAX = Number.MAX_SAFE_INTEGER;
// function parse_id(maybe_id: number): Id {
//     if (maybe_id < 0) throw new Error("Id cannot be negative");
//     if (maybe_id > ID_MAX) throw new Error(`Id cannot exceed '${ID_MAX}'`);
//     if (!Number.isInteger(maybe_id)) throw new Error("Id cannot have a decimal"); // Fallback

//     return maybe_id as Id
// }

// // https://www.slingacademy.com/article/mastering-regular-expressions-in-typescript/
// type Name = string & { readonly _name: true };
// function parse_name(maybe_name: string): Name {
//     if (maybe_name.length == 0) throw new Error("Name cannot be empty");
//     if (maybe_name.length > maybe_name.trim().length) throw new Error("Name cannot begin or end with empty space");
//     if (/\s{2,}/.test(maybe_name)) throw new Error("Name cannot contain consecutive empty space");

//     return maybe_name as Name
// }

// type Brand = string & { readonly _brand: true };
// function parse_brand(maybe_brand: string): Brand {
//     if (maybe_brand.length == 0) throw new Error("Brand cannot be empty");
//     if (maybe_brand.length > maybe_brand.trim().length) throw new Error("Brand cannot begin or end with empty space");
//     if (/\s{2,}/.test(maybe_brand)) throw new Error("Brand cannot contain consecutive empty space");

//     return maybe_brand as Brand
// }

// type Tag = string & { readonly _tag: true };
// function parse_tag(maybe_tag: string): Tag {
//     if (maybe_tag.length == 0) throw new Error("Tag cannot be empty");
//     if (maybe_tag.length > maybe_tag.trim().length) throw new Error("Tag cannot begin or end with empty space");
//     if (/\s{2,}/.test(maybe_tag)) throw new Error("Tag cannot contain consecutive empty space");

//     return maybe_tag as Tag
// }

// type Quantity = number & { readonly _quantity: true };
// const QUANTITY_DEFAULT = 1 as Quantity;
// const QUANTITY_MAX = Number.MAX_SAFE_INTEGER;
// function parse_quantity(maybe_quantity: number): Quantity {
//     if (maybe_quantity < 0) throw new Error("Quantity cannot be negative");
//     if (maybe_quantity > ID_MAX) throw new Error(`Quantity cannot exceed '${QUANTITY_MAX}'`);
//     if (!Number.isInteger(maybe_quantity)) throw new Error("Quantity cannot have a decimal"); // Fallback

//     return maybe_quantity as Quantity
// }

function AddItem() {
    const [id, set_id] = useState<number | undefined>(undefined);
    const [name, set_name] = useState<string | undefined>(undefined);
    const [brand, set_brand] = useState<string | undefined>(undefined);
    const [tags, set_tags] = useState(new Set<string>());
    const [quantity, set_quantity] = useState(1);

    const [id_raw, set_id_raw] = useState("");
    const [name_raw, set_name_raw] = useState("");
    const [brand_raw, set_brand_raw] = useState("");
    // TODO: tags and brand

    const [id_err, set_id_err] = useState<string | undefined>(undefined);
    const [name_err, set_name_err] = useState<string | undefined>(undefined);
    const [brand_err, set_brand_err] = useState<string | undefined>(undefined);
    const [tags_err, set_tags_err] = useState<string | undefined>(undefined);
    const [quantity_err, set_quantity_err] = useState<string | undefined>(undefined);

    // https://www.geeksforgeeks.org/reactjs/react-onchange-event/
    // https://www.w3tutorials.net/blog/only-numbers-input-number-in-react/
    const on_id_change = (raw: string) => {
        if (/[^0-9]/.test(raw)) {
            set_id_err("Can only contain the digits 0-9");
        } else if (raw.length > 16) {
            set_id_err("Cannot exceed 16 digits");
        } else {
            set_id_err(undefined);
        }

        set_id_raw(raw);
    };

    const on_name_change = (raw: string) => {
        if (raw.length == 0) {
            set_name_err("Cannot be empty");
        } else {
            set_name_err(undefined);
        }

        set_name_raw(raw);
    };

    const on_brand_change = (raw: string) => {
        set_brand_raw(raw);
    };

    const on_add = () => {
        // If there are any errors, abort
        if (id_err || name_err || brand_err || tags_err || quantity_err) return;
    };

    // Run at first render
    useEffect(() => {
        on_id_change(id_raw);
        on_name_change(name_raw);
        on_brand_change(brand_raw);
    }, []);
    
    // https://html.spec.whatwg.org/multipage/interaction.html#input-modalities:-the-inputmode-attribute
    return (
        <div id="add-item-container">
            <div id="add-item-title">Add Item</div>
            <div id="add-item-body">
                <form id="add-item-fields">
                    <label className="add-item-field">
                        <>Id: </>
                        <input className="add-item-field-text-input" placeholder="unspecified" value={id_raw} onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                            on_id_change(event.target.value);
                        }}></input>
                        {id_err && <span style={{ color: "red" }}> {id_err}</span>}
                    </label>
                    <label className="add-item-field">
                        <>Name: </>
                        <input className="add-item-field-text-input" value={name_raw} onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                            on_name_change(event.target.value);
                        }}></input>
                        <span style={{ color: "red" }}> *</span>
                        {name_err && <span style={{ color: "red" }}> {name_err}</span>}
                    </label>
                    <label className="add-item-field">
                        <>Brand: </>
                        <input className="add-item-field-text-input" placeholder="unspecified" value={brand_raw} onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                            on_brand_change(event.target.value);
                        }}></input>
                        {brand_err && <span style={{ color: "red" }}> {brand_err}</span>}
                    </label>
                    <label className="add-item-field">
                        <>Tags: </>
                        <b>TODO</b>
                        {tags_err && <span style={{ color: "red" }}> {tags_err}</span>}
                    </label>
                    <label className="add-item-field">
                        <>Quantity: </>
                        <b>TODO</b>
                        {quantity_err && <span style={{ color: "red" }}> {quantity_err}</span>}
                    </label>
                </form>
                <div id="add-item-buttons">
                    {/* add-item-scan-barcode-button */}
                    {/* add-item-existing-product-button */}
                    <button type="button" onClick={on_add}>
                        Add
                    </button>
                </div>
            </div>
        </div>
    );
}

export default AddItem;
