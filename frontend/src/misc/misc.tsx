export function unreachable(err_msg: string): never {
    throw new Error(`UNREACHABLE CODE TRIGGERED: '${err_msg}'`);
}

export type Nullable<T> = T | null | undefined;

export class Option<T> {
  private value: Nullable<T>

  constructor(value: Nullable<T>) {
    this.value = value
  }

  map<U>(fn: (v: T) => U): Option<U> {
    if (this.value) {
        return new Option(fn(this.value))
    }
    
    return new Option<U>(null)
  }

  into_inner(): Nullable<T> {
    return this.value
  }

  unwrap(): T {
    return this.expect("Called unwrap on None")
  }

  expect(msg: string): T {
    if (this.value) {
        return this.value
    }

    throw new Error(msg)
  }

  is_some(): boolean {
    return this.value !== null && this.value !== undefined
  }

  is_none(): boolean {
    return !this.is_some()
  }

  static none<U>(): Option<U> {
    return new Option<U>(null)
  }

  static some<U>(value: U): Option<U> {
    return new Option<U>(value)
  }
}
