import { BrowserMultiFormatOneDReader, type IScannerControls } from "@zxing/browser";
import { useCallback, useEffect, useRef, useState } from "react";

const NON_DIGIT = /[^0-9]/; // https://www.w3tutorials.net/blog/only-numbers-input-number-in-react/
const LEADING_TRAILING_WHITESPACE = /^\s|\s$/; // https://stackoverflow.com/questions/10351644/regular-expression-to-check-whitespace-in-the-beginning-and-end-of-a-string
const CONSECUTIVE_WHITESPACE = /\s{2,}/;

function AddItem() {
    const [id_raw, set_id_raw] = useState("");
    const [name_raw, set_name_raw] = useState("");
    const [brand_raw, set_brand_raw] = useState("");
    const [tags, set_tags] = useState(new Set<string>());
    const [quantity, set_quantity] = useState(1);

    const [id_err, set_id_err] = useState<string | null>(null);
    const [name_err, set_name_err] = useState<string | null>(null);
    const [brand_err, set_brand_err] = useState<string | null>(null);
    const [tags_err, set_tags_err] = useState<string | null>(null);
    const [quantity_err, set_quantity_err] = useState<string | null>(null);

    const [barcode_scanner_enabled, set_barcode_scanner_enabled] = useState(false);
    const video_ref = useRef<HTMLVideoElement>(null);
    const barcode_reader_ref = useRef<BrowserMultiFormatOneDReader>(null);
    const barcode_reader_controls_ref = useRef<IScannerControls>(null);

    const [existing_product_lookup_enabled, set_existing_product_lookup_enabled] = useState(false);

    // https://www.geeksforgeeks.org/reactjs/react-onchange-event/
    const on_id_change = (raw: string) => {
        if (NON_DIGIT.test(raw)) {
            set_id_err("Can only contain the digits 0-9");
        } else if (raw.length > 16) {
            set_id_err("Cannot exceed 16 digits");
        } else {
            set_id_err(null);
        }

        set_id_raw(raw);
    };

    const on_name_change = (raw: string) => {
        if (raw.length == 0) {
            set_name_err("Cannot be empty");
        } else if (LEADING_TRAILING_WHITESPACE.test(raw)) {
            set_name_err("Cannot begin or end with empty space");
        } else if (CONSECUTIVE_WHITESPACE.test(raw)) {
            set_name_err("Cannot contain consecutive empty space");
        } else {
            set_name_err(null);
        }

        set_name_raw(raw);
    };

    const on_brand_change = (raw: string) => {
        if (LEADING_TRAILING_WHITESPACE.test(raw)) {
            set_brand_err("Cannot begin or end with empty space");
        } else if (CONSECUTIVE_WHITESPACE.test(raw)) {
            set_brand_err("Cannot contain consecutive empty space");
        } else {
            set_brand_err(null);
        }

        set_brand_raw(raw);
    };

    const start_barcode_scanner = () => {
        const barcode_reader = new BrowserMultiFormatOneDReader();
        barcode_reader_ref.current = barcode_reader;

        barcode_reader.decodeFromVideoDevice(
            undefined,
            video_ref.current!,
            (res, err) => {
                if (res) {
                    set_id_raw(res.getText());
                    set_barcode_scanner_enabled(false);
                } if (err && err.name != "NotFoundException2") {
                    console.error(err);
                }
            }
        ).then(controls => {
            barcode_reader_controls_ref.current = controls;
        }).catch(console.error);
    }

    const stop_barcode_scanner = () => {
        barcode_reader_controls_ref.current?.stop();
    }

    const on_scan_barcode_clicked = () => {
        set_barcode_scanner_enabled(true);
    }

    const on_select_existing_product_clicked = () => {

    }

    const form_err_exists = (): boolean => {
        if (id_err || name_err || brand_err || tags_err || quantity_err) {
            return true;
        }

        return false;
    }

    const on_add_clicked = () => {
        // If there are any errors, abort
        if (form_err_exists()) return;

        // TODO: add new item
    };

    useEffect(() => {
        if (barcode_scanner_enabled) {
            start_barcode_scanner();
        } else {
            stop_barcode_scanner();
        }
    }, [barcode_scanner_enabled]);

    // Run at first render
    useEffect(() => {
        on_id_change(id_raw);
        on_name_change(name_raw);
        on_brand_change(brand_raw);
    }, []);
    
    // https://html.spec.whatwg.org/multipage/interaction.html#input-modalities:-the-inputmode-attribute
    return (
        <>
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
                        <button type="button" onClick={on_scan_barcode_clicked} disabled={barcode_scanner_enabled}>
                            Scan Barcode
                        </button>
                        <button type="button" onClick={on_select_existing_product_clicked} disabled={existing_product_lookup_enabled}>
                            Select Existing Product
                        </button>
                        <button type="button" onClick={on_add_clicked} disabled={form_err_exists()}>
                            Add
                        </button>
                    </div>
                </div>
            </div>
            {barcode_scanner_enabled &&
                <div id="barcode-scanner">
                    <div id="barcode-scanner-title">Scan a Barcode</div>
                    <video ref={video_ref} id="barcode-scanner-video"/>
                </div>
            }
        </>
    );
}

export default AddItem;
