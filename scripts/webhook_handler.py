#!/usr/bin/env python3
# Lightweight webhook receiver for OpenCanary alerts
from flask import Flask, request, jsonify
import subprocess, os, json

app = Flask(__name__)
APP_DIR = os.getenv('APP_DIR', '/opt/yunohost/apps/decoy_watch')

@app.route('/webhook', methods=['POST'])
def handle_alert():
    data = request.json
    # Filter for high-value events
    if data.get('logdata', {}).get('ATTACK_DATA', {}).get('username') or \
       'backup' in json.dumps(data).lower() or \
       data.get('logdata', {}).get('REQUEST', '').startswith('GET /admin'):
        
        msg = f"Network decoy triggered: {data.get('src_host')} -> {data.get('logdata', {})}"
        # Call unified notifier
        subprocess.run([
            f"{APP_DIR}/scripts/notify.sh",
            "🔥 Network Honeypot Alert",
            msg,
            "critical"
        ], check=False)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    # Run on localhost only - nginx proxies external requests
    app.run(host='127.0.0.1', port=int(os.getenv('WEBHOOK_PORT', 18080)))