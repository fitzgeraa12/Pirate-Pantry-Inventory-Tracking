export interface FieldProperties {
    as: React.ElementType;
    id?: string;
    className?: string;
}

// https://www.robinwieruch.de/react-as-prop/
// https://blog.logrocket.com/react-children-prop-typescript/
function Field({ as: Tag, id, className, children }: React.PropsWithChildren<FieldProperties>) {
    const fieldClass = "add-item-field"

    // If custom class was passed in, add our tag as well, otherwise just set as our tag
    const classNameFull = className ? `${className} ${fieldClass}` : fieldClass
    
    return (
        <Tag id={id} className={classNameFull}>
            {children}
        </Tag>
    );
}

export default Field;
