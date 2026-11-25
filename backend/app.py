import os
import socket
from datetime import datetime, timezone
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

messages = [
    {
        "id": 1,
        "text": "Backend service initialized",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

@app.route("/healthz", methods=["GET"])
def health():
    return jsonify({"status": "ok", "host": socket.gethostname()})

@app.route("/api/info", methods=["GET"])
def info():
    return jsonify({
        "app": os.getenv("APP_NAME", "backend-api"),
        "env": os.getenv("ENVIRONMENT", "production"),
        "port": os.getenv("PORT", "5000"),
        "host": socket.gethostname(),
        "client_ip": request.remote_addr,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@app.route("/api/messages", methods=["GET"])
def list_messages():
    return jsonify({
        "host": socket.gethostname(),
        "count": len(messages),
        "data": messages
    })

@app.route("/api/messages", methods=["POST"])
def create_message():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "text field is required"}), 400

    item = {
        "id": len(messages) + 1,
        "text": text,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    messages.append(item)
    return jsonify({"status": "created", "host": socket.gethostname(), "data": item}), 201

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
