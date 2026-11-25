import os
import socket
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

PORT = int(os.getenv("PORT", 8080))
APP_NAME = os.getenv("APP_NAME", "frontend-web")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:5000").rstrip("/")

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        host=socket.gethostname(),
        backend_url=BACKEND_PUBLIC_URL
    )

@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok", "host": socket.gethostname()})

@app.route("/api/ping-backend", methods=["GET"])
def ping_backend():
    url = f"{BACKEND_PUBLIC_URL}/api/info"
    try:
        res = requests.get(url, timeout=4)
        return jsonify({
            "status": "success",
            "url": url,
            "status_code": res.status_code,
            "payload": res.json()
        })
    except Exception as e:
        return jsonify({"status": "error", "url": url, "error": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
