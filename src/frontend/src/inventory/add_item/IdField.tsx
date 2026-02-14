import Field, { type FieldProperties } from "./Field";

function IdField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Id
        </Field>
    );
}

export default IdField;
