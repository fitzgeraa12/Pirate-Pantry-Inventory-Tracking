import React from "react";

interface TitledProps {
    title: string,
}

export default function Titled({ title, children }: React.PropsWithChildren<TitledProps>): React.ReactNode {
    React.useEffect(() => {
        document.title = title;
    }, [])
    
    return (
        <>
            {children}
        </>
    );
}
