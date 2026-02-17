import Titled from "./Titled";

function Unauthorized() {
    return (
        <Titled title="Unauthorized">
            <div style={{ color: "white", fontWeight: "bold", justifySelf: "center" }}>
                UNAUTHORIZED
            </div>
        </Titled>
    );
}

export default Unauthorized;
