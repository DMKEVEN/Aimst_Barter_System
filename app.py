import os
import json
import time
import threading
import requests as http_requests
from flask import Flask, render_template_string, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from PIL import Image


# =========================================================================
# PENDO SERVER-SIDE TRACK EVENT HELPER
# =========================================================================
PENDO_TRACK_URL = "https://data.pendo.io/data/track"
PENDO_INTEGRATION_KEY = "5a06d1b8-9002-4c90-b78b-bca79cd76054"


def pendo_track(event_name, visitor_id, properties=None, account_id="aimst_barter_system"):
    """Send a track event to Pendo's server-side API. Runs in a background thread to avoid blocking requests."""
    payload = {
        "type": "track",
        "event": event_name,
        "visitorId": visitor_id or "anonymous",
        "accountId": account_id,
        "timestamp": int(time.time() * 1000),
        "properties": properties or {}
    }

    def _send():
        try:
            http_requests.post(
                PENDO_TRACK_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-pendo-integration-key": PENDO_INTEGRATION_KEY
                },
                timeout=5
            )
        except Exception as e:
            print(f"Pendo track event error ({event_name}): {e}")

    threading.Thread(target=_send, daemon=True).start()

app = Flask(__name__)

# =========================================================================
# 🛡️ CORE SYSTEMS & SECURITY CONFIGURATION
# =========================================================================
app.secret_key = "AIMST_SECURE_SUPER_SECRET_KEY_2026_MASTER_PURGE_3D"
ADMIN_PASSWORD = "Taarieven2006"

# Dynamic absolute paths to prevent file tracking errors on any hard drive
base_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(base_dir, 'static', 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DATA_FILE = os.path.join(base_dir, 'marketplace_data.json')
USER_FILE = os.path.join(base_dir, 'users_registry.json')

# =========================================================================
# 🔑 PERSISTENT USER REGISTRY STORAGE CONTROLLERS
# =========================================================================
def load_user_registry():
    """Loads users from the hard drive json file so they never get wiped."""
    default_users = [
        {
            "username": "keven_admin",
            "full_name": "Keventhiran A/L Devandren",
            "student_id": "E25101420",
            "phone": "+60 12-638-4757",
            "password": "Taarieven2006"
        },
        {
            "username": "taarisini_admin",
            "full_name": "Taarisini A/P Selvakumar",
            "student_id": "E25101220",
            "phone": "+60 11-6411-6483",
            "password": "Taarieven2006"
        }
    ]

    if not os.path.exists(USER_FILE):
        save_user_registry(default_users)
        return default_users

    try:
        with open(USER_FILE, 'r') as f:
            disk_users = json.load(f)

        if not isinstance(disk_users, list):
            disk_users = default_users

        updated = False

        for default_user in default_users:
            found = False
            for user in disk_users:
                if user["username"] == default_user["username"]:
                    found = True
                    if user["password"] != default_user["password"]:
                        user["password"] = default_user["password"]
                        updated = True
                    break
            if not found:
                disk_users.append(default_user)
                updated = True

        if updated:
            save_user_registry(disk_users)

        return disk_users
    except Exception:
        return default_users

def save_user_registry(user_list):
    """Saves users directly to hard drive instantly."""
    try:
        with open(USER_FILE, 'w') as f:
            json.dump(user_list, f, indent=4)
    except Exception as e:
        print(f"User registry save error: {e}")

# =========================================================================
# 💾 MARKETPLACE DATA STORAGE CONTROLLERS
# =========================================================================
def load_marketplace_data():
    if not os.path.exists(DATA_FILE):
        initial_data = [
            {
                "id": 0,
                "student": "keven_admin",
                "item": "Mechanical Keyboard (Blue Switches)",
                "looking_for": "Type-C Fast Charging Cable",
                "contact": "012-638-4757",
                "status": "Available",
                "image_file": "default_item.jpg"
            }
        ]
        save_marketplace_data(initial_data)
        return initial_data
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return []

def save_marketplace_data(data_list):
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data_list, f, indent=4)
    except Exception as e:
        print(f"Data commit error layer: {e}")


# =========================================================================
# 🤖 AUTONOMOUS AI MATCHING AGENT ENGINE
# =========================================================================
def calculate_ai_agent_matches(feed):
    """
    Autonomous heuristic intelligence agent. 
    Scans the live campus data arrays, finds bidirectional overlaps between 
    what users have vs what they want, and isolates high-value trade loops.
    """
    ai_alerts = []
    available_items = [i for i in feed if i.get("status") == "Available"]
    
    # Text Analysis Helper
    def extract_keywords(text):
        return set(text.lower().replace("(", "").replace(")", "").replace("-", " ").split())

    # Double structural matching sequence
    for i, item_a in enumerate(available_items):
        for item_b in available_items[i+1:]:
            if item_a["student"] == item_b["student"]:
                continue
            
            # Extract word sets to find overlap matches
            have_a = extract_keywords(item_a["item"])
            want_a = extract_keywords(item_a["looking_for"])
            
            have_b = extract_keywords(item_b["item"])
            want_b = extract_keywords(item_b["looking_for"])
            
            # Check if Item A matches what Owner B wants, AND Item B matches what Owner A wants
            match_1 = len(have_a.intersection(want_b)) > 0 or item_a["item"].lower().strip() in item_b["looking_for"].lower().strip()
            match_2 = len(have_b.intersection(want_a)) > 0 or item_b["item"].lower().strip() in item_a["looking_for"].lower().strip()
            
            if match_1 and match_2:
                ai_alerts.append({
                    "user_1": item_a["student"],
                    "item_1": item_a["item"],
                    "user_2": item_b["student"],
                    "item_2": item_b["item"]
                })
    if ai_alerts:
        matched_users = list({m["user_1"] for m in ai_alerts} | {m["user_2"] for m in ai_alerts})
        matched_items = list({m["item_1"] for m in ai_alerts} | {m["item_2"] for m in ai_alerts})
        pendo_track("ai_trade_match_discovered", "system", {
            "match_count": len(ai_alerts),
            "matched_users": ", ".join(matched_users[:10]),
            "matched_items": ", ".join(matched_items[:5]),
            "available_items_scanned": len(available_items)
        })
    return ai_alerts


# =========================================================================
# 🎨 PROFESSIONAL FRONTEND TEMPLATES (HTML/CSS)
# =========================================================================
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SECURE ACCESS PORTAL - AIMST Barter System</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <script>
    (function(apiKey){
        (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
        v=['initialize','identify','updateOptions','pageLoad','track', 'trackAgent'];for(w=0,x=v.length;w<x;++w)(function(m){
        o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
        y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
        z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');
    })('63f1477e-1fc8-4c8f-8143-959187ef3ba4');
    </script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eceff1; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 15px; box-sizing: border-box; }
        .security-wrapper { background: white; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); width: 100%; max-width: 440px; padding: 25px 20px; box-sizing: border-box; }
        .branding-dock { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 25px; background: #f1f5f9; padding: 10px; border-radius: 8px; border: 1px solid #e2e8f0; box-sizing: border-box; }
        .dock-left-col { display: flex; align-items: center; gap: 8px; border-right: 1px solid #cbd5e1; padding-right: 4px; }
        .dock-right-col { display: flex; align-items: center; justify-content: flex-end; gap: 8px; padding-left: 4px; }
        .dock-logo { width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.08); flex-shrink: 0; }
        .dock-label { font-size: 10px; text-align: left; color: #64748b; font-weight: 600; line-height: 1.2; word-break: keep-all; }
        .dock-label span { color: #00796b; display: block; font-size: 11px; font-weight: 700; }
        .secure-vault-area { text-align: center; margin-bottom: 25px; }
        .logo-vault-circle { width: 140px; height: 140px; margin: 0 auto 15px auto; border-radius: 50%; background: white; border: 4px solid #00796b; box-sizing: border-box; display: flex; align-items: center; justify-content: center; overflow: hidden; box-shadow: 0 4px 10px rgba(0, 121, 107, 0.15); transition: all 0.3s ease; }
        .actual-site-logo { width: 100%; height: 100%; object-fit: cover; }
        @keyframes securityAura { 0% { border-color: #00796b; box-shadow: 0 4px 10px rgba(0, 121, 107, 0.15); } 50% { border-color: #004d40; box-shadow: 0 0 18px rgba(0, 77, 64, 0.35); } 100% { border-color: #00796b; box-shadow: 0 4px 10px rgba(0, 121, 107, 0.15); } }
        .security-access-active .logo-vault-circle { animation: securityAura 1.4s infinite ease-in-out; }
        h1 { margin: 5px 0 2px 0; font-size: 22px; font-weight: bold; color: #004d40; text-align: center; }
        .slogan-english { font-size: 12px; color: #64748b; text-align: center; font-weight: 600; letter-spacing: 0.5px; }
        .form-group { text-align: left; margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; color: #334155; font-size: 14px; }
        input[type="text"], input[type="password"] { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; box-sizing: border-box; font-size: 15px; transition: all 0.3s ease; background: #ffffff; }
        input:focus { border-color: #00796b; box-shadow: 0 0 0 3px rgba(0, 121, 107, 0.15); outline: none; }
        .btn-login { background: #00796b; color: white; border: none; padding: 13px; width: 100%; font-size: 15px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; transition: background 0.2s; }
        .btn-login:hover { background: #004d40; }
        .msg-error { color: #b91c1c; font-weight: bold; margin-bottom: 15px; font-size: 14px; text-align: center; }
        @media (max-width: 360px) { .dock-label { font-size: 9px; } .dock-label span { font-size: 10px; } }
    </style>
</head>
<body>
    <div class="security-wrapper" id="securityWrapper">
        <div class="branding-dock">
            <div class="dock-left-col">
                <img class="dock-logo" src="/static/images/Taarieven_logo.jpg" alt="Taarieven">
                <div class="dock-label">Powered By:<span>Taarieven</span></div>
            </div>
            <div class="dock-right-col">
                <div class="dock-label" style="text-align: right;">Specialized For:<span>AIMST University</span></div>
                <img class="dock-logo" src="/static/images/Aimst.jpg" alt="AIMST">
            </div>
        </div>

        <div class="secure-vault-area">
            <div class="logo-vault-circle">
                <img class="actual-site-logo" src="/static/images/Aimst_Barter_System_Logo.jpg" alt="AIMST Barter System 1.0">
            </div>
            <h1>AIMST Barter System 1.0</h1>
            <div class="slogan-english">Your trash, their treasure. Smart trading for AIMST.</div>
        </div>
        {% if error_msg %}
            <div class="msg-error">❌ {{ error_msg }}</div>
        {% endif %}
        <form action="/login" method="POST">
            <div class="form-group">
                <label>System Username:</label>
                <input type="text" name="username" placeholder="Enter username" required>
            </div>
            <div class="form-group">
                <label>Account Password:</label>
                <input type="password" name="password" id="passwordField" placeholder="Enter password" required onfocus="activateSecurityAnimation()" onblur="deactivateSecurityAnimation()">
            </div>
            <button type="submit" class="btn-login">Authenticate Session</button>
        </form>
    </div>
    <script>
        function activateSecurityAnimation() { document.getElementById('securityWrapper').classList.add('security-access-active'); }
        function deactivateSecurityAnimation() { document.getElementById('securityWrapper').classList.remove('security-access-active'); }

        pendo.initialize({
            visitor: {
                id: ''
            }
        });
    </script>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AIMST Barter System 1.0 - Campus Exchange Network</title>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <script>
    (function(apiKey){
        (function(p,e,n,d,o){var v,w,x,y,z;o=p[d]=p[d]||{};o._q=o._q||[];
        v=['initialize','identify','updateOptions','pageLoad','track', 'trackAgent'];for(w=0,x=v.length;w<x;++w)(function(m){
        o[m]=o[m]||function(){o._q[m===v[0]?'unshift':'push']([m].concat([].slice.call(arguments,0)));};})(v[w]);
        y=e.createElement(n);y.async=!0;y.src='https://cdn.pendo.io/agent/static/'+apiKey+'/pendo.js';
        z=e.getElementsByTagName(n)[0];z.parentNode.insertBefore(y,z);})(window,document,'script','pendo');
    })('63f1477e-1fc8-4c8f-8143-959187ef3ba4');
    </script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f9; color: #333; margin: 0; padding: 20px; padding-bottom: 60px; }
        .container { max-width: 800px; margin: 0 auto; }
        header { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 15px; margin-bottom: 30px; background: #004d40; color: white; padding: 30px 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .header-logo-circle-container { width: 130px; height: 130px; border-radius: 50%; background: white; padding: 4px; box-shadow: 0 4px 8px rgba(0,0,0,0.15); display: flex; align-items: center; justify-content: center; overflow: hidden; border: 3px solid #00796b; }
        .header-logo-circle-container img { width: 100%; height: 100%; object-fit: cover; border-radius: 50%; }
        .header-text h1 { margin: 5px 0 0 0; font-size: 26px; letter-spacing: 0.5px; font-weight: bold; }
        .slogan-english { font-size: 13px; opacity: 0.85; margin: 6px 0 0 0; font-weight: 600; letter-spacing: 0.5px; }
        .user-badge { background: #00796b; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: bold; border: 1px solid #b2dfdb; width: 90%; max-width: fit-content; box-sizing: border-box; margin-bottom: 5px; }
        .user-badge.founder-badge-style { background: #b58900 !important; border: 1px solid #ffc107 !important; }
        .user-badge a { color: #ffc107; text-decoration: none; margin-left: 8px; }
        
        /* 🤖 AI AGENT DESIGNS */
        .ai-agent-card { background: #e0f7fa; border: 2px dashed #00acc1; padding: 20px; border-radius: 10px; margin-bottom: 25px; box-shadow: 0 4px 10px rgba(0, 172, 193, 0.1); }
        .ai-title-row { font-size: 16px; font-weight: bold; color: #006064; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
        .ai-match-alert { background: white; border-left: 5px solid #00b0ff; padding: 12px; margin-bottom: 10px; border-radius: 4px; font-size: 14px; color: #37474f; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }
        .ai-match-alert strong { color: #007cb3; }

        .system-formal-notice { background: #fff3e0; border-left: 6px solid #e65100; padding: 16px 20px; border-radius: 8px; box-shadow: 0 3px 6px rgba(0,0,0,0.05); margin-bottom: 25px; box-sizing: border-box; }
        .notice-title-row { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: bold; color: #e65100; margin-bottom: 5px; }
        .notice-body-text { font-size: 14px; color: #4e342e; line-height: 1.5; margin: 0; font-weight: 500; }
        .notice-body-text strong { color: #d84315; font-weight: 700; }
        .card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px; }
        h2 { margin-top: 0; color: #004d40; border-bottom: 2px solid #e0f2f1; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: bold; margin-bottom: 5px; }
        input[type="text"], input[type="password"], input[type="file"] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; font-size: 16px; background: white; }
        input[readonly] { background-color: #f1f3f4; color: #5f6368; cursor: not-allowed; border: 1px dashed #00796b; font-weight: 500; }
        .btn-primary { background: #00796b; color: white; border: none; padding: 12px 20px; font-size: 16px; border-radius: 4px; cursor: pointer; width: 100%; font-weight: bold; }
        .btn-primary:hover { background: #004d40; }
        .action-container { margin-top: 15px; background: #f5f5f5; padding: 10px; border-radius: 4px; border: 1px solid #ddd; }
        .input-inline { width: 100% !important; padding: 8px !important; font-size: 14px !important; margin-bottom: 10px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box; }
        .btn-swap { background: #e65100; color: white; padding: 10px; font-size: 14px; border-radius: 4px; cursor: pointer; font-weight: bold; border: none; width: 100%; text-align: center; }
        .btn-swap:hover { background: #b53d00; }
        .btn-delete { background: #c62828; color: white; padding: 8px; font-size: 13px; border-radius: 4px; cursor: pointer; font-weight: bold; border: none; width: 100%; text-align: center; }
        .btn-delete:hover { background: #8e1c1c; }
        .item-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media(max-width: 600px) { .item-grid { grid-template-columns: 1fr; } }
        .item-card { background: #e0f2f1; border-left: 5px solid #00796b; padding: 15px; border-radius: 4px; display: flex; flex-direction: column; justify-content: space-between; }
        .item-card.swapped { background: #eaeaea; border-left: 5px solid #757575; opacity: 0.85; }
        .item-img { width: 100%; height: 180px; object-fit: cover; border-radius: 4px; margin-bottom: 10px; background: #b2dfdb; border: 1px solid #b2dfdb; }
        .item-title { font-size: 18px; font-weight: bold; color: #004d40; margin-top: 5px; }
        .item-card.swapped .item-title { color: #555; text-decoration: line-through; }
        .trade-for { margin-top: 10px; font-style: italic; color: #555; }
        .contact-box { margin-top: 15px; background: white; padding: 8px; border-radius: 4px; font-size: 14px; border: 1px dashed #00796b; color: #004d40; }
        .item-card.swapped .contact-box { display: none; }
        .student-tag { font-size: 12px; background: #004d40; color: white; padding: 3px 8px; border-radius: 12px; float: right; font-weight: bold; }
        .item-card.swapped .student-tag { background: #616161; }
        .swapped-badge { display: block; background: #d32f2f; color: white; font-size: 13px; font-weight: bold; padding: 6px; text-align: center; border-radius: 4px; margin-bottom: 10px; }
        .msg-error { color: #c62828; font-size: 14px; font-weight: bold; margin-top: 5px; text-align: center; }
        .msg-success { color: #2e7d32; font-size: 14px; font-weight: bold; margin-top: 5px; text-align: center; }
        .mentor-box { text-align: center; background: #e0f2f1; padding: 20px; border-radius: 8px; border: 2px solid #00796b; margin-bottom: 25px; }
        .mentor-quote { font-style: italic; color: #004d40; font-size: 16px; margin-top: 10px; font-weight: 500; }
        .founders-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: center; margin-top: 20px; }
        @media(max-width: 600px) { .founders-grid { grid-template-columns: 1fr; } }
        .founder-profile { background: #f9f9f9; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; }
        .profile-img { width: 130px; height: 130px; border-radius: 50%; object-fit: cover; background: #ccc; margin: 0 auto 15px auto; border: 3px solid #00796b; display: block; }
        .admin-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px; }
        .admin-table th, .admin-table td { border: 1px solid #ddd; padding: 12px 10px; text-align: left; }
        .admin-table th { background-color: #004d40; color: white; }
        .btn-terminate { background-color: #c62828; color: white; border: none; padding: 8px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px; display: inline-flex; align-items: center; justify-content: center; }
        .btn-view-info { background-color: #00796b; color: white; border: none; padding: 8px 10px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px; margin-top: 4px; display: inline-block; }
        .btn-view-info:hover { background-color: #004d40; }
        .hidden-detail-row { display: none; background-color: #f8fafc; }
        .detail-card { padding: 12px; border: 1px solid #cbd5e1; border-radius: 6px; background: white; margin: 5px 0; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
        .detail-item { font-size: 13px; color: #334155; margin-bottom: 6px; }
        .detail-item:last-child { margin-bottom: 0; }
        .detail-item strong { color: #004d40; }
        .search-box-container { margin-bottom: 15px; position: relative; }
        .search-input { padding: 12px 12px 12px 35px !important; border: 2px solid #00796b !important; border-radius: 6px !important; font-size: 15px !important; }
        .search-icon-label { position: absolute; left: 12px; top: 12px; color: #00796b; font-weight: bold; font-size: 16px; }
        .secure-modal-backdrop { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.6); z-index: 9999; justify-content: center; align-items: center; }
        .secure-modal-box { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.25); width: 100%; max-width: 420px; border-top: 6px solid #c62828; box-sizing: border-box; text-align: center; }
        .modal-btn-group { display: flex; gap: 10px; margin-top: 20px; }
        .btn-modal-confirm { background: #c62828; color: white; border: none; padding: 10px 15px; font-weight: bold; border-radius: 4px; cursor: pointer; flex: 1; }
        .btn-modal-cancel { background: #9e9e9e; color: white; border: none; padding: 10px 15px; font-weight: bold; border-radius: 4px; cursor: pointer; flex: 1; }
        footer { font-size: 13px; color: #757575; text-align: center; margin-top: 30px; padding: 15px; background: white; border-radius: 8px; border-top: 3px solid #004d40; }
        footer span { font-weight: bold; color: #00796b; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="user-badge">
                {% if current_user %}
                    {% if current_user == 'keven_admin' or current_user == 'taarisini_admin' %}
                        <div class="user-badge founder-badge-style">👑 Founder: {{ current_user }} | <a href="/logout" onclick="pendo.clearSession()" style="color: #fff; font-weight: bold;">Logout</a></div>
                    {% else %}
                        <div class="user-badge">👤 Session: {{ current_user }} | <a href="/logout" onclick="pendo.clearSession()">Logout</a></div>
                    {% endif %}
                {% else %}
                    <div class="user-badge">👤 Mode: Guest | <a href="/login_page" style="color: #ffc107;">Login to Upload</a></div>
                {% endif %}
            </div>
            <div class="header-logo-circle-container">
                <img src="/static/images/Aimst_Barter_System_Logo.jpg" alt="AIMST Barter System 1.0">
            </div>
            <div class="header-text">
                <h1>AIMST Barter System 1.0</h1>
                <div class="slogan-english">Your trash, their treasure. Smart trading for AIMST</div>
            </div>
        </header>

        <div class="ai-agent-card">
            <div class="ai-title-row">🤖 AUTONOMOUS AI MATCHING AGENT ACTIVE</div>
            {% if ai_matches %}
                {% for match in ai_matches %}
                    <div class="ai-match-alert">
                        🎯 **Trade Loop Discovered:** **@{{ match.user_1 }}** has a *{{ match.item_1 }}* which matches perfectly with what **@{{ match.user_2 }}** (*{{ match.item_2 }}*) wants to exchange!
                    </div>
                {% endfor %}
            {% else %}
                <p style="margin: 0; font-size: 13px; color: #546e7a; font-style: italic;">AI Agent parsing matrix coordinates... No active dual trade loops found on campus yet.</p>
            {% endif %}
        </div>

        <div class="system-formal-notice">
            <div class="notice-title-row">🔑 OFFICIAL CAMPUS DIRECTIVE NOTICE</div>
            <p class="notice-body-text">
                Security Policy Restriction: If you want to list items or upload media to this platform, you must operate a verified whitelisted student profile. To request credential assignment, please formally contact the Lead Systems Integrator, <strong>Keventhiran Devandren at +60 12-638-4757</strong>, to complete identity clearance.
            </p>
        </div>

        {% if error_msg %}
            <div class="card" style="border: 2px solid #c62828;">
                <div class="msg-error">❌ {{ error_msg }}</div>
            </div>
        {% endif %}
        {% if success_msg %}
            <div class="card" style="border: 2px solid #2e7d32;">
                <div class="msg-success">✅ {{ success_msg }}</div>
            </div>
        {% endif %}

        {% if current_user == 'keven_admin' or current_user == 'taarisini_admin' %}
        <div class="card" style="border: 2px solid #00796b;">
            <h2 style="color: #004d40;">➕ Add New Student to Whitelist Registry</h2>
            <form action="/add_student" method="POST">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div class="form-group">
                        <label>Custom Username:</label>
                        <input type="text" name="reg_username" placeholder="e.g. jame_cs" required>
                    </div>
                    <div class="form-group">
                        <label>Student Full Name:</label>
                        <input type="text" name="reg_full_name" placeholder="e.g. James Peterson" required>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;">
                    <div class="form-group">
                        <label>AIMST Student ID:</label>
                        <input type="text" name="reg_student_id" placeholder="e.g. E25101500" required>
                    </div>
                    <div class="form-group">
                        <label>Phone Number/email:</label>
                        <input type="text" name="reg_phone" placeholder="e.g. 017-1234567" required>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;">
                    <div class="form-group">
                        <label>Assigned Login Password:</label>
                        <input type="text" name="reg_password" placeholder="Set default password" required>
                    </div>
                    <div class="form-group">
                        <label style="color: #c62828;">Master Admin Password:</label>
                        <input type="password" name="admin_key" placeholder="Enter admin key to commit" style="border: 1px solid #c62828;" required>
                    </div>
                </div>
                <button type="submit" class="btn-primary" style="background: #004d40; margin-top: 15px;">Securely Register Student to Hard Disk</button>
            </form>
        </div>
        {% endif %}

        <div class="card">
            <h2>📤 List an Unwanted Item</h2>
            <form action="/upload" method="POST" enctype="multipart/form-data">
                <div class="form-group">
                    <label>What are you giving away?</label>
                    <input type="text" name="item" placeholder="e.g. Unused iPad Case" required>
                </div>
                <div class="form-group">
                    <label>What do you want in exchange?</label>
                    <input type="text" name="looking_for" placeholder="e.g. Wireless Mouse" required>
                </div>
                <div class="form-group">
                    <label>Contact Info:</label>
                    {% if current_phone %}
                        <input type="text" name="contact" value="{{ current_phone }}" readonly required>
                    {% else %}
                        <input type="text" placeholder="🔒 Please log in to bind your registered contact details" readonly required>
                    {% endif %}
                </div>
                <div class="form-group">
                    <label>Upload Item Image (Optional):</label>
                    <input type="file" name="item_image" accept="image/*">
                </div>
                <button type="submit" class="btn-primary">Publish to Campus Live Feed</button>
            </form>
        </div>

        <div class="card">
            <h2>🌐 Live Campus Marketplace Feed ({{ items|length }} Total Items)</h2>
            <div class="item-grid">
                {% for item in items %}
                <div class="item-card {% if item.status == 'Swapped' %}swapped{% endif %}">
                    <div>
                        {% if item.image_file == 'default_item.jpg' %}
                            <div class="item-img" style="display: flex; align-items: center; justify-content: center; font-weight: bold; color: #00796b;">No Image Given</div>
                        {% else %}
                            <img class="item-img" src="/static/images/{{ item.image_file }}" alt="Item image">
                        {% endif %}
                        <span class="student-tag">By: @{{ item.student }}</span>
                        <div class="item-title">🎁 {{ item.item }}</div>
                        <div class="trade-for">🔍 Looking to swap for: <strong>{{ item.looking_for }}</strong></div>
                    </div>
                    <div>
                        {% if item.status == 'Available' %}
                            <div class="contact-box">📞 <strong>Secure Contact:</strong> {{ item.contact }}</div>
                            <div class="action-container">
                                <form action="/action/{{ item.id }}" method="POST">
                                    <input type="password" name="user_auth_password" class="input-inline" placeholder="Enter account password to swap..." required>
                                    <button type="submit" name="action_type" value="swap" class="btn-swap">🤝 Mark as Swapped</button>
                                </form>
                            </div>
                        {% else %}
                            <div class="swapped-badge">Deal Completed / Swapped</div>
                            <div class="action-container" style="background: #ffebee;">
                                <form action="/action/{{ item.id }}" method="POST">
                                    <input type="password" name="user_auth_password" class="input-inline" placeholder="Enter account password to delete..." required>
                                    <button type="submit" name="action_type" value="delete" class="btn-delete">🗑️ Remove Permanently</button>
                                </form>
                            </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>📤 Our Pillars of Inspiration</h2>
            <div class="mentor-box">
                <img class="profile-img" src="/static/images/raman.jpg" alt="Mr Raman Raguraman">
                <div style="font-size: 20px; font-weight: bold; color: #004d40;">Mr. Raman Raguraman</div>
                <div style="font-size: 14px; color: #555; font-weight: 600; margin-top: 2px;">Dean of Faculty of Engineering and Computer Technology</div>
                <p class="mentor-quote">"Inspiring us to increase system optimization and reduce operational costs."</p>
            </div>
            <h3 style="color: #004d40; text-align: center; margin-top: 30px; border-top: 1px solid #e0f2f1; padding-top: 20px;">System Core Developers</h3>
            <div class="founders-grid">
                <div class="founder-profile">
                    <img class="profile-img" src="/static/images/taarisini.jpg" alt="Taarisini Selvakumar">
                    <div style="font-size: 18px; font-weight: bold; color: #004d40;">Taarisini Selvakumar</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Co-Founder & Lead UI/UX Product Manager<br>Bachelor in Computer Science<br>(Aimst University)</div>
                </div>
                <div class="founder-profile">
                    <img class="profile-img" src="/static/images/keven.jpg" alt="Keventhiran Devandren">
                    <div style="font-size: 18px; font-weight: bold; color: #004d40;">Keventhiran Devandren</div>
                    <div style="font-size: 14px; color: #666; font-style: italic;">Co-Founder & Lead Systems Integrator<br>Bachelor in Computer Science<br>(Aimst University)</div>
                </div>
            </div>
        </div>

        {% if registry %}
        <div class="card" style="border-top: 4px solid #004d40;">
            <h2>📋 AIMST Verified Whitelist Registry Log</h2>
            <div class="search-box-container">
                <span class="search-icon-label">🔍</span>
                <input type="text" id="registrySearchInput" class="search-input" onkeyup="filterRegistryTable()" placeholder="Query username pattern...">
            </div>
            <table class="admin-table" id="registryTable">
                <thead>
                    <tr>
                        <th>Whitelisted Student Accounts</th>
                        <th style="width: 110px; text-align: center;">Controls</th>
                    </tr>
                </thead>
                <tbody>
                    {% for student in registry %}
                    <tr class="student-master-row">
                        <td class="username-cell">
                            <strong>@{{ student.username }}</strong>
                            <br>
                            <button type="button" class="btn-view-info" onclick="toggleStudentDetails('detail_{{ student.username }}')">👁️ View Profile</button>
                        </td>
                        <td style="text-align: center; vertical-align: middle;">
                            {% if current_user in ['keven_admin', 'taarisini_admin'] %}
                                <button type="button" class="btn-terminate" onclick="openSecureTerminationModal('{{ student.username }}')">❌ Out</button>
                            {% else %}
                                <span style="font-size: 11px; color: #94a3b8; font-weight: bold;">🔒 Restricted</span>
                            {% endif %}
                        </td>
                    </tr>
                    <tr id="detail_{{ student.username }}" class="hidden-detail-row">
                        <td colspan="2">
                            <div class="detail-card">
                                <div class="detail-item"><strong>Full Name:</strong> {{ student.full_name }}</div>
                                
                                {% if current_user in ['keven_admin', 'taarisini_admin'] or student.username == current_user %}
                                    <div class="detail-item"><strong>Student ID:</strong> <code>{{ student.student_id }}</code></div>
                                    <div class="detail-item"><strong>Contact No:</strong> {{ student.phone }}</div>
                                {% elif student.has_uploaded %}
                                    <div class="detail-item"><strong>Student ID:</strong> <span style="color:#94a3b8; font-style:italic; font-size:12px;">🔒 Hidden for Security</span></div>
                                    <div class="detail-item"><strong>Contact No:</strong> {{ student.phone }}</div>
                                {% else %}
                                    <div class="detail-item"><strong>Student ID:</strong> <span style="color:#94a3b8; font-style:italic; font-size:12px;">🔒 Hidden for Security</span></div>
                                    <div class="detail-item"><strong>Contact No:</strong> <span style="color:#e65100; font-weight:600; font-size:12px;">🔒 Hidden (No active uploads)</span></div>
                                {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
    </div>

    <footer>
        ⚡ Powered by <span>Taarieven</span> | Exclusive for <span>AIMST University</span>
    </footer>

    <div id="terminationModalOverlay" class="secure-modal-backdrop">
        <div class="secure-modal-box">
            <h3>🔒 CRITICAL SECURITY AUTHORIZATION</h3>
            <p style="font-size: 14px; color: #333; margin-bottom: 15px; text-align: left;">
                You are executing a permanent core user account termination for account profile: <strong id="modalTargetUsernameText" style="color: #c62828;"></strong>.
            </p>
            <form id="secureTerminationForm" action="" method="POST">
                <div style="text-align: left; margin-bottom: 15px;">
                    <label style="font-weight: bold; font-size: 13px; display: block; margin-bottom: 5px;">Enter Master Admin Key:</label>
                    <input type="password" name="admin_verification_password" placeholder="••••••••" style="width: 100%; padding: 10px; border-radius: 4px; border: 1px solid #ccc; box-sizing: border-box;" required>
                </div>
                <div class="modal-btn-group">
                    <button type="button" class="btn-modal-cancel" onclick="closeSecureTerminationModal()">Cancel</button>
                    <button type="submit" class="btn-modal-confirm">Confirm Terminate</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        function toggleStudentDetails(rowId) {
            var targetRow = document.getElementById(rowId);
            if (targetRow.style.display === "table-row") {
                targetRow.style.display = "none";
            } else {
                targetRow.style.display = "table-row";
            }
        }

        function filterRegistryTable() {
            var input = document.getElementById("registrySearchInput");
            var filter = input.value.toLowerCase().trim().replace('@', '');
            var table = document.getElementById("registryTable");
            var masterRows = table.getElementsByClassName("student-master-row");

            for (var i = 0; i < masterRows.length; i++) {
                var td = masterRows[i].getElementsByClassName("username-cell")[0];
                if (td) {
                    var txtValue = td.textContent || td.innerText;
                    var nextRow = masterRows[i].nextElementSibling;
                    var detailRow = (nextRow && nextRow.classList.contains("hidden-detail-row")) ? nextRow : null;

                    if (txtValue.toLowerCase().indexOf(filter) > -1) {
                        masterRows[i].style.display = "";
                    } else {
                        masterRows[i].style.display = "none";
                        if(detailRow) detailRow.style.display = "none";
                    }
                }
            }
        }

        function openSecureTerminationModal(username) {
            document.getElementById("modalTargetUsernameText").innerText = "@" + username;
            document.getElementById("secureTerminationForm").action = "/terminate/" + username;
            document.getElementById("terminationModalOverlay").style.display = "flex";
        }
        function closeSecureTerminationModal() {
            document.getElementById("terminationModalOverlay").style.display = "none";
            document.getElementById("secureTerminationForm").reset();
        }

        pendo.initialize({
            visitor: {
                id: ''
            }
        });
        {% if current_user %}
        pendo.identify({
            visitor: {
                id: {{ current_user|tojson }},
                full_name: {{ current_full_name|tojson }},
                student_id: {{ current_student_id|tojson }},
                phone: {{ current_phone|tojson }}
            }
        });
        {% endif %}
    </script>
</body>
</html>
"""

# =========================================================================
# 🔀 APPLICATION ROUTING CONTROLLERS
# =========================================================================
@app.route("/")
def home():
    error_msg = request.args.get("error_msg")
    success_msg = request.args.get("success_msg")
    current_user = session.get("user")
    current_phone = None
    current_full_name = None
    current_student_id = None

    # Load active data sets from the persistent text files
    all_raw_students = load_user_registry()
    active_feed = load_marketplace_data()

    # Execute the Autonomous AI Agent Layer Matching Algorithm on current listings
    ai_matches = calculate_ai_agent_matches(active_feed)

    # Determine which students have uploaded functional items with an 'Available' status
    active_uploaders = {item["student"] for item in active_feed if item.get("status") == "Available"}

    # Establish custom runtime visibility filters for our UI data stream
    processed_registry = []
    for student in all_raw_students:
        username = student["username"]
        has_uploaded = username in active_uploaders

        # Check visibility settings dynamically
        is_founder = current_user in ["keven_admin", "taarisini_admin"]
        is_owner = username == current_user

        # If an anonymous guest visits and the user has no active uploads, skip rendering
        if not current_user and not has_uploaded:
            continue

        # Add tracking variable flags directly to user objects for the rendering layout
        student_copy = dict(student)
        student_copy["has_uploaded"] = has_uploaded
        processed_registry.append(student_copy)

        if is_owner:
            current_phone = student["phone"]
            current_full_name = student["full_name"]
            current_student_id = student["student_id"]

    return render_template_string(
        HTML_TEMPLATE, 
        items=active_feed, 
        error_msg=error_msg, 
        success_msg=success_msg, 
        current_user=current_user,
        registry=processed_registry,
        current_phone=current_phone,
        current_full_name=current_full_name,
        current_student_id=current_student_id,
        ai_matches=ai_matches
    )

@app.route("/login_page")
def login_page():
    return render_template_string(LOGIN_TEMPLATE, error_msg=request.args.get("error_msg"))

@app.route("/login", methods=["POST"])
def process_login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    current_registry = load_user_registry()
    user_authenticated = False
    for student in current_registry:
        if student["username"] == username and student["password"] == password:
            user_authenticated = True
            break
    if user_authenticated:
        session["user"] = username
        is_admin = username in ["keven_admin", "taarisini_admin"]
        pendo_track("user_login_completed", username, {
            "username": username,
            "is_admin": is_admin,
            "login_method": "form"
        })
        return redirect(url_for("home", success_msg="Authenticated successfully! Welcome back."))
    else:
        pendo_track("user_login_failed", "anonymous", {
            "attempted_username": username,
            "failure_reason": "invalid_credentials"
        })
        return redirect(url_for("login_page", error_msg="Authentication Failed! Incorrect Username or Password."))

@app.route("/logout")
def process_logout():
    session.pop("user", None)
    return redirect(url_for("home", success_msg="Logged out successfully."))

@app.route("/add_student", methods=["POST"])
def add_student():
    current_user = session.get("user")
    if current_user not in ["keven_admin", "taarisini_admin"]:
        pendo_track("user_registration_failed", current_user or "anonymous", {
            "attempted_by": current_user or "anonymous",
            "failure_reason": "insufficient_permissions"
        })
        return redirect(url_for("home", error_msg="Access Denied: Only Founders can authorize registry additions."))

    admin_key_input = request.form.get("admin_key")
    if admin_key_input != ADMIN_PASSWORD:
        pendo_track("user_registration_failed", current_user, {
            "attempted_by": current_user,
            "failure_reason": "incorrect_admin_password"
        })
        return redirect(url_for("home", error_msg="Registry Breach Aborted! Incorrect Master Admin Password."))

    username = request.form.get("reg_username", "").strip().lower()
    full_name = request.form.get("reg_full_name", "").strip()
    student_id = request.form.get("reg_student_id", "").strip()
    phone = request.form.get("reg_phone", "").strip()
    password = request.form.get("reg_password", "")

    current_registry = load_user_registry()

    for student in current_registry:
        if student["username"] == username:
            pendo_track("user_registration_failed", current_user, {
                "attempted_username": username,
                "attempted_by": current_user,
                "failure_reason": "duplicate_username"
            })
            return redirect(url_for("home", error_msg=f"Registration aborted: Username @{username} already exists."))

    current_registry.append({
        "username": username,
        "full_name": full_name,
        "student_id": student_id,
        "phone": phone,
        "password": password
    })

    save_user_registry(current_registry)
    pendo_track("user_registered", current_user, {
        "new_username": username,
        "student_id": student_id,
        "registered_by": current_user,
        "total_users_count": len(current_registry)
    })
    return redirect(url_for("home", success_msg=f"Successfully whitelisted @{username} to persistent disk storage!"))

@app.route("/terminate/<string:target_username>", methods=["POST"])
def terminate_user(target_username):
    if "user" not in session:
        return redirect(url_for("login_page", error_msg="Please log in to perform administrative actions."))
    verification_input = request.form.get("admin_verification_password")
    if verification_input != ADMIN_PASSWORD:
        return redirect(url_for("home", error_msg="Administrative Breach Denied! Incorrect Master Access Key."))
    if target_username == session["user"]:
        return redirect(url_for("home", error_msg="System Protection Override: You cannot terminate your own active session!"))

    current_registry = load_user_registry()
    for index, student in enumerate(current_registry):
        if student["username"] == target_username:
            current_registry.pop(index)
            save_user_registry(current_registry)

            current_feed = load_marketplace_data()
            items_removed = len([item for item in current_feed if item["student"] == target_username])
            updated_feed = [item for item in current_feed if item["student"] != target_username]
            save_marketplace_data(updated_feed)
            pendo_track("user_terminated", session["user"], {
                "terminated_username": target_username,
                "terminated_by": session["user"],
                "items_removed_count": items_removed,
                "remaining_users_count": len(current_registry)
            })
            return redirect(url_for("home", success_msg=f"Administrative Action Complete: Profile @{target_username} successfully purged."))
    return redirect(url_for("home", error_msg="Target profile trace identifier not found."))

@app.route("/upload", methods=["POST"])
def upload_item():
    if "user" not in session:
        return redirect(url_for("login_page", error_msg="Security Notice: You must log in before publishing a listing!"))
    current_feed = load_marketplace_data()
    if len(current_feed) > 0:
        next_item_id = max([item["id"] for item in current_feed]) + 1
    else:
        next_item_id = 1
    item = request.form.get("item")
    looking_for = request.form.get("looking_for")
    contact = request.form.get("contact")
    file = request.files.get('item_image')
    filename = "default_item.jpg"
    image_processing_success = None
    original_file_format = None
    if file and file.filename != '':
        filename = f"upload_{next_item_id}.jpg"
        original_file_format = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else "unknown"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        upload_path = os.path.join(base_dir, 'static', 'images', filename)
        try:
            img = Image.open(file)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((800, 800))
            img.save(upload_path, "JPEG", quality=70, optimize=True)
            image_processing_success = True
        except Exception as e:
            file.seek(0)
            file.save(upload_path)
            image_processing_success = False
        pendo_track("item_image_uploaded", session["user"], {
            "item_id": next_item_id,
            "filename": filename,
            "image_processing_success": image_processing_success,
            "original_file_format": original_file_format,
            "username": session["user"]
        })
    current_feed.append({
        "id": next_item_id,
        "student": session["user"],
        "item": item,
        "looking_for": looking_for,
        "contact": contact,
        "status": "Available",
        "image_file": filename
    })
    save_marketplace_data(current_feed)
    pendo_track("item_listed", session["user"], {
        "item_id": next_item_id,
        "item_name": item,
        "looking_for": looking_for,
        "has_image": filename != "default_item.jpg",
        "username": session["user"],
        "total_listings_count": len(current_feed)
    })
    return redirect(url_for("home", success_msg="Item published successfully to the campus live feed!"))

@app.route("/action/<int:item_id>", methods=["POST"])
def item_action(item_id):
    if "user" not in session:
        return redirect(url_for("login_page", error_msg="Please log in to manage marketplace actions."))
    user_password_input = request.form.get("user_auth_password")
    action_type = request.form.get("action_type")
    current_logged_in_user = session["user"]
    current_feed = load_marketplace_data()
    current_registry = load_user_registry()

    for index, item in enumerate(current_feed):
        if item["id"] == item_id:
            if user_password_input == ADMIN_PASSWORD:
                if action_type == "delete":
                    pendo_track("item_deleted", current_logged_in_user, {
                        "item_id": item_id,
                        "item_name": item.get("item", ""),
                        "item_owner": item.get("student", ""),
                        "deleted_by": current_logged_in_user,
                        "is_admin_action": True,
                        "item_status_before_delete": item.get("status", "")
                    })
                    current_feed.pop(index)
                    save_marketplace_data(current_feed)
                    return redirect(url_for("home", success_msg="Administrative action: Item successfully purged."))
                elif action_type == "swap":
                    item["status"] = "Swapped"
                    save_marketplace_data(current_feed)
                    pendo_track("item_swap_completed", current_logged_in_user, {
                        "item_id": item_id,
                        "item_name": item.get("item", ""),
                        "looking_for": item.get("looking_for", ""),
                        "item_owner": item.get("student", ""),
                        "action_performed_by": current_logged_in_user,
                        "is_admin_action": True
                    })
                    return redirect(url_for("home", success_msg="Administrative action: Status overridden to Swapped."))
            registered_password = None
            for student in current_registry:
                if student["username"] == current_logged_in_user:
                    registered_password = student["password"]
                    break
            if item["student"] != current_logged_in_user:
                return redirect(url_for("home", error_msg="Access Denied! You are not authorized to modify another student's listing."))
            if user_password_input == registered_password:
                if action_type == "swap":
                    item["status"] = "Swapped"
                    save_marketplace_data(current_feed)
                    pendo_track("item_swap_completed", current_logged_in_user, {
                        "item_id": item_id,
                        "item_name": item.get("item", ""),
                        "looking_for": item.get("looking_for", ""),
                        "item_owner": item.get("student", ""),
                        "action_performed_by": current_logged_in_user,
                        "is_admin_action": False
                    })
                    return redirect(url_for("home", success_msg="Listing status successfully updated to Swapped!"))
                elif action_type == "delete":
                    if item["status"] == "Swapped":
                        pendo_track("item_deleted", current_logged_in_user, {
                            "item_id": item_id,
                            "item_name": item.get("item", ""),
                            "item_owner": item.get("student", ""),
                            "deleted_by": current_logged_in_user,
                            "is_admin_action": False,
                            "item_status_before_delete": "Swapped"
                        })
                        current_feed.pop(index)
                        save_marketplace_data(current_feed)
                        return redirect(url_for("home", success_msg="Your completed listing has been removed from the log."))
                    else:
                        return redirect(url_for("home", error_msg="Access Denied! Standard users can only delete items marked as Swapped."))
            else:
                return redirect(url_for("home", error_msg="Authentication Failed! Incorrect account password."))
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=9000)