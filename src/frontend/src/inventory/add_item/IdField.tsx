import Field, { type FieldProperties } from "./Field";

// https://react.dev/reference/react-dom/components/input
function IdField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            <label>
                Id: 
                <input name="id" placeholder="unspecified" type="number" className="add-item-field-text-input"/>
            </label>
        </Field>
    );
}

export default IdField;
