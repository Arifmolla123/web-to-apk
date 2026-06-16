from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
import io
import re
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

# ---------- নতুন যোগ করা রুট (ইউজার ইন্টারফেস দেখানোর জন্য) ----------
@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

@app.route('/script.js')
def serve_js():
    return send_file('script.js')
# ---------- যোগ করা অংশ শেষ ----------

@app.route('/generate-apk', methods=['POST'])
def generate_apk():
    # Get form data
    website_url = request.form.get('url')
    app_name = request.form.get('name')
    app_icon = request.files.get('icon')

    if not website_url or not app_name or not app_icon:
        return {"error": "Missing form data"}, 400

    # Prepare data for pwa2apk.com API
    files = {
        'icon': (app_icon.filename, app_icon.stream, app_icon.content_type)
    }
    data = {
        'url': website_url,
        'name': app_name
    }

    try:
        pwa2apk_response = requests.post('https://pwa2apk.com/api/generate', data=data, files=files, stream=True)
        pwa2apk_response.raise_for_status()  # Raise an exception for bad status codes

        # Get the filename from the content-disposition header if available, otherwise default
        filename = "app.apk"
        if "content-disposition" in pwa2apk_response.headers:
            content_disposition = pwa2apk_response.headers["content-disposition"]
            # Extract filename* if present, otherwise filename
            filename_match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition)
            if filename_match:
                filename = unquote(filename_match.group(1))
            else:
                filename_match = re.search(r"filename=\"?([^;\"]+)\"?", content_disposition)
                if filename_match:
                    filename = filename_match.group(1)

        # Send the APK file back to the client
        return send_file(
            io.BytesIO(pwa2apk_response.content),
            mimetype=pwa2apk_response.headers['Content-Type'],
            as_attachment=True,
            download_name=filename
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling pwa2apk.com API: {e}")
        return {"error": f"Failed to generate APK from external API: {e}"}, 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected server error occurred: {e}"}, 500

# ---------- সবচেয়ে গুরুত্বপূর্ণ পরিবর্তন (Render-এর জন্য পোর্ট বাইন্ডিং) ----------
if __name__ == '__main__':
    # Render চলাকালীন PORT এনভায়রনমেন্ট ভেরিয়েবল থেকে পোর্ট নাও, নাহলে ৫০০০ ধরো
    port = int(os.environ.get("PORT", 5000))
    # 0.0.0.0-এ বাইন্ড করো, যাতে Render বাইরে থেকে সংযোগ পায়
    app.run(host='0.0.0.0', port=port)