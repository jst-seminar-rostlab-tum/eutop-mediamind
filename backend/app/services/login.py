import argparse
import json
from app.services.hardcoded_login import hardcoded_login

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Login to a specified newspaper or all newspapers.')
    parser.add_argument('newspaper_key', type=str, nargs='?', help='Key of the newspaper to log in (optional).')
    args = parser.parse_args()

    if args.newspaper_key:
        key = args.newspaper_key
        success = hardcoded_login(key)
        if success:
            print(f"Login for {key} successful.")
        else:
            print(f"Login for {key} failed.")
    else:
        with open('app/services/newspapers_data.json', 'r') as f:
            data = json.load(f)
            for key in data['newspapers']:
                print(f"Trying login for {key}...")
                success = hardcoded_login(key)
                if success:
                    print(f"Login for {key} successful.")
                else:
                    print(f"Login for {key} failed.")
