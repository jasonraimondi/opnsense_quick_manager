import os

from flask import Flask, send_file
from lib.opnsense_api import OpnsenseClient, OpnsenseApi

HOST = os.getenv("OPNSENSE_HOST")
API_KEY = os.getenv("OPNSENSE_API_KEY")
API_SECRET = os.getenv("OPNSENSE_API_SECRET")

client = OpnsenseClient(HOST, API_KEY, API_SECRET)
api = OpnsenseApi(client)

app = Flask(__name__)

@app.context_processor
def inject_globals():
    return {
        'HOST': HOST,
        'APP_NAME': "OPNsense Manager",
        # You can even add functions
        'is_production': lambda: os.getenv('FLASK_ENV') == 'production'
    }

@app.route("/")
def index():
    return send_file('templates/index.html')

@app.route("/status")
def get_status():
    try:
        enabled = api.get_blocklist_status()
        return {"status": "success", "enabled": enabled}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/enable")
def enable_blocklist():
    try:
        api.toggle_unbound_blocklist(True)
        return {"status": "success"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

@app.route("/disable")
def disable_blocklist():
    try:
        api.toggle_unbound_blocklist(False)
        return {"status": "success"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500