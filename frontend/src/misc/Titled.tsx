import { useEffect, type PropsWithChildren } from "react";

function Titled({ title, children }: PropsWithChildren<{ title: string }>) {
    useEffect(() => {
        document.title = `Pirate Pantry - ${title}`;
    }, [])
    
    return (
        <>{children}</>
    );
}

export default Titled;
