import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dotenv
import api
import database

def main():
    valid_args = {"--local"}
    unknown = [arg for arg in sys.argv[1:] if arg not in valid_args]
    if unknown:
        print(f"Unknown arguments: {' '.join(unknown)}")
        sys.exit(1)

    is_local = "--local" in sys.argv
    if is_local:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.local")
        dotenv.load_dotenv(env_path)

    db = database.connect(is_local)
    api.host(db, is_local)

if __name__ == "__main__":
    main()