import Field, { type FieldProperties } from "./Field";

function NameField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            <label>
                Name: <input name="name" placeholder={"e.g. \"Life Cereal\""} type="text" required={true} className="add-item-field-text-input"/> <span style={{ color: "red" }}>*</span>
            </label>
        </Field>
    );
}

export default NameField;