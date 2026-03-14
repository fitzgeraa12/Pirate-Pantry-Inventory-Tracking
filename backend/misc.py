import os

def env_get(var_name: str) -> str:
    val = os.environ.get(var_name)
    assert val is not None

    return val
