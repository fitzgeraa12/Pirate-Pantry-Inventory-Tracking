import Field, { type FieldProperties } from "./Field";

function QuantityField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Quantity
        </Field>
    );
}

export default QuantityField;
