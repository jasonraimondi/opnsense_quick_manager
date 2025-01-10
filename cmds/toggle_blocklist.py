import os
from datetime import datetime
from lib.opnsense_api import OpnsenseApi, OpnsenseClient


def log(message):
    print(f"[{datetime.now()}] UNBOUND: {message}")

def main():
    HOST = os.getenv("OPNSENSE_HOST")
    API_KEY = os.getenv("OPNSENSE_API_KEY")
    API_SECRET = os.getenv("OPNSENSE_API_SECRET")

    client = OpnsenseClient(HOST, API_KEY, API_SECRET)
    api = OpnsenseApi(client)

    try:
        blocklist_enabled = api.get_blocklist_status()
        log(f"blocklist is {'enabled' if blocklist_enabled else 'disabled'}")

        if blocklist_enabled:
            log(f"disabling blocklist...")
            api.toggle_unbound_blocklist(False)
            log(f"blocklist disabled successfully")
            return "disabled"
        else:
            log(f"enabling blocklist...")
            api.toggle_unbound_blocklist(True)
            log(f"enabled successfully")
            return "enabled"
    except Exception as e:
        log(f"Error: {str(e)}")

if __name__ == "__main__":
    main()