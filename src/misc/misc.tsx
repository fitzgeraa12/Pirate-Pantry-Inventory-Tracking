export function unreachable(err_msg: string): never {
    throw new Error(`UNREACHABLE CODE TRIGGERED: '${err_msg}'`);
}
