import os
import sys
import psutil
import shutil
import winreg
import tempfile
from pathlib import Path

def clear_temp_folders():
    temp_paths = [
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
        os.path.join(os.environ.get('LOCALAPPDATA'), 'Temp'),
        os.path.join(os.environ.get('APPDATA'), 'Temp')
    ]
    
    for temp_path in temp_paths:
        if temp_path and os.path.exists(temp_path):
            for item in os.listdir(temp_path):
                try:
                    item_path = os.path.join(temp_path, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path, ignore_errors=True)
                except:
                    continue

def clear_python_cache():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for root, dirs, files in os.walk(os.path.expanduser('~'), topdown=False):
        if root.startswith(current_dir):
            continue
        for name in dirs:
            if name == '__pycache__':
                try:
                    cache_dir = os.path.join(root, name)
                    shutil.rmtree(cache_dir)
                except:
                    continue

def clear_pip_cache():
    try:
        import pip
        pip_cache = os.path.join(os.path.expanduser('~'), '.cache', 'pip')
        if os.path.exists(pip_cache):
            shutil.rmtree(pip_cache)
    except:
        pass

def kill_process():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() in ['gamebypass.exe', 'system_service.exe']:
                try:
                    proc.kill()
                except:
                    pass
    except:
        pass

def remove_files():
    targets = [
        'GameBypass.exe',
        'system_service.exe',
        'GameBypass.spec',
        '.device_id'
    ]
    
    paths = [
        os.environ.get('TEMP'),
        os.environ.get('TMP'),
        os.environ.get('APPDATA'),
        os.path.join(os.environ.get('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup'),
        os.getcwd()
    ]
    
    for path in paths:
        if path:
            for target in targets:
                try:
                    target_path = os.path.join(path, target)
                    if os.path.exists(target_path):
                        os.remove(target_path)
                except:
                    continue

def clear_registry():
    keys = [
        (winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
        (winreg.HKEY_LOCAL_MACHINE, "Software\\Microsoft\\Windows\\CurrentVersion\\Run")
    ]
    
    for hkey, path in keys:
        try:
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_ALL_ACCESS) as key:
                try:
                    winreg.DeleteValue(key, "GameBypass")
                    winreg.DeleteValue(key, "system_service")
                except:
                    pass
        except:
            pass

def remove_build_folders():
    folders = ['build', 'dist', '__pycache__']
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    for folder in folders:
        try:
            folder_path = os.path.join(current_dir, folder)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except:
            pass

def clear_logs():
    log_paths = [
        os.path.join(os.environ.get('APPDATA'), 'logs'),
        os.path.join(os.environ.get('LOCALAPPDATA'), 'logs')
    ]
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            try:
                shutil.rmtree(log_path)
            except:
                continue

def main():
    print("🧹 Iniciando limpieza profunda...")
    
    print("Terminando procesos...")
    kill_process()
    
    print("Eliminando archivos...")
    remove_files()
    
    print("Limpiando registro...")
    clear_registry()
    
    print("Eliminando archivos temporales...")
    remove_build_folders()
    
    print("Limpiando caché de Python...")
    clear_python_cache()
    
    print("Limpiando caché de pip...")
    clear_pip_cache()
    
    print("Limpiando registro del sistema...")
    clear_registry()
    
    print("Limpiando logs...")
    clear_logs()
    
    print("\n✅ Limpieza completada!")
    input("\nPresione Enter para salir...")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPresione Enter para salir...")
