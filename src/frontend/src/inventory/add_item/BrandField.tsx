import Field, { type FieldProperties } from "./Field";

function BrandField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Brand: <input name="name" placeholder="unspecified" type="text" required={true} className="add-item-field-text-input"/>
        </Field>
    );
}

export default BrandField;
