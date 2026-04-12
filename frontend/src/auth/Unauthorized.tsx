import Titled from "../misc/Titled";

function Unauthorized() {
    return (
        <Titled title="Pirate Pantry - UNAUTHORIZED">
            <div style={{ color: "white", fontWeight: "bold", justifySelf: "center" }}>
                UNAUTHORIZED
            </div>
        </Titled>
    );
}

export default Unauthorized;
