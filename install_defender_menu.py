import sys
import ctypes
import winreg
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def install_menu():
    menu_name = "Add to Defender Exclusions"
    # The command still needs to use PowerShell to call Add-MpPreference
    # We use a nested PowerShell call to ensure it runs elevated when clicked
    ps_command = (
        "powershell.exe -WindowStyle Hidden -Command "
        "\"Start-Process powershell.exe -Verb RunAs -ArgumentList "
        "'-NoProfile -Command Add-MpPreference -ExclusionPath ''%1'''\""
    )
    
    icon_path = r"C:\Program Files\Windows Defender\EppManifest.dll,-101"

    # Targets: Files (*) and Directories (Directory)
    targets = [
        r"Software\Classes\*\shell\DefenderExclusion",
        r"Software\Classes\Directory\shell\DefenderExclusion"
    ]

    try:
        for key_path in targets:
            print(f"Adding key: HKLM\\{key_path}")
            
            # Create the main key
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "", 0, winreg.REG_SZ, menu_name)
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            
            # Create the command subkey
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, f"{key_path}\\command") as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, ps_command)
                
        print("\nSuccess! Context menu added.")
        print("Right-click a file or folder and look for 'Add to Defender Exclusions'.")
        
    except PermissionError:
        print("\nError: Access Denied. Please ensure the script is running as Administrator.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    if is_admin():
        install_menu()
        input("\nPress Enter to exit...")
    else:
        print("Requesting Administrator privileges...")
        run_as_admin()
