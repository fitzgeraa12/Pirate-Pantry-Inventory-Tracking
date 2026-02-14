import Field, { type FieldProperties } from "./Field";

function BrandField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Brand
        </Field>
    );
}

export default BrandField;
