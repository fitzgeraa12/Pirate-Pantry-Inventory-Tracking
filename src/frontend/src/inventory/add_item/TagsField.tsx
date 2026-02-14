import Field, { type FieldProperties } from "./Field";

function TagsField({as: Tag = "li", id, className}: FieldProperties) {
    return (
        <Field as={Tag} id={id} className={className}>
            Tags
        </Field>
    );
}

export default TagsField;