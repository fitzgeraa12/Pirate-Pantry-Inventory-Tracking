import Field, { type FieldProperties } from "./Field";

function NameField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Name
        </Field>
    );
}

export default NameField;