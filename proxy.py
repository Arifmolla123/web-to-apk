from flask import Flask, request, send_file
from flask_cors import CORS
import requests
import os
import io
import re
from urllib.parse import unquote

app = Flask(__name__)
CORS(app)

# ফ্রন্টএন্ড ফাইল সার্ভ করার রুট
@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

@app.route('/script.js')
def serve_js():
    return send_file('script.js')

@app.route('/generate-apk', methods=['POST'])
def generate_apk():
    website_url = request.form.get('url')
    app_name = request.form.get('name')
    app_icon = request.files.get('icon')

    if not website_url or not app_name or not app_icon:
        return {"error": "Missing form data"}, 400

    files = {
        'icon': (app_icon.filename, app_icon.stream, app_icon.content_type)
    }
    data = {
        'url': website_url,
        'name': app_name
    }

    try:
        pwa2apk_response = requests.post('https://pwa2apk.com/api/generate', data=data, files=files, stream=True)
        
        # লগিং: API কী রিটার্ন করছে দেখুন
        app.logger.info(f"Status Code: {pwa2apk_response.status_code}")
        app.logger.info(f"Content-Type: {pwa2apk_response.headers.get('Content-Type')}")
        # রেসপন্সের প্রথম ৫০০ অক্ষর লগ করুন (যদি টেক্সট হয়)
        app.logger.info(f"Response preview: {pwa2apk_response.text[:500]}")
        
        pwa2apk_response.raise_for_status()

        # কন্টেন্ট-টাইপ যাচাই
        content_type = pwa2apk_response.headers.get('Content-Type', '')
        if 'application/vnd.android.package-archive' not in content_type:
            app.logger.error(f"Unexpected Content-Type: {content_type}")
            app.logger.error(f"Response text: {pwa2apk_response.text[:500]}")
            return {"error": f"API did not return an APK. It returned: {content_type}"}, 500

        filename = "app.apk"
        if "content-disposition" in pwa2apk_response.headers:
            content_disposition = pwa2apk_response.headers["content-disposition"]
            filename_match = re.search(r"filename\*=UTF-8''([^;]+)", content_disposition)
            if filename_match:
                filename = unquote(filename_match.group(1))
            else:
                filename_match = re.search(r"filename=\"?([^;\"]+)\"?", content_disposition)
                if filename_match:
                    filename = filename_match.group(1)

        return send_file(
            io.BytesIO(pwa2apk_response.content),
            mimetype='application/vnd.android.package-archive',
            as_attachment=True,
            download_name=filename
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error calling pwa2apk.com API: {e}")
        return {"error": f"Failed to generate APK from external API: {e}"}, 500
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return {"error": f"An unexpected server error occurred: {e}"}, 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)