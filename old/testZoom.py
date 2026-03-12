import tkinter as tk
import os
import time
import keyboard

def setup_final_registry():
    print("1. Killing ZoomIt...")
    os.system("taskkill /f /im ZoomIt.exe >nul 2>&1")
    os.system("taskkill /f /im ZoomIt64.exe >nul 2>&1")
    time.sleep(1)

    print("2. Injecting PERFECT Keys (Ctrl+Shift+1/2/3)...")
    
    keys = {
        "ToggleKey": 817,           # Ctrl+Shift+1 (Zoom)
        "DrawToggleKey": 818,       # Ctrl+Shift+2 (Draw) - המפתח האמיתי שעלינו עליו!
        "LiveZoomToggleKey": 819,   # Ctrl+Shift+3 (Live Zoom)
        "LiveZoomKey": 819,
        "OptionsShown": 1,          # מונע קפיצה של ההגדרות
        "ShowTrayIcon": 1
    }

    paths = [
        r"HKCU\Software\Sysinternals\ZoomIt",
        r"HKCU\Software\Sysinternals\ZoomIt64"
    ]

    for path in paths:
        os.system(f'reg add "{path}" /v EulaAccepted /t REG_DWORD /d 1 /f /reg:64 >nul 2>&1')
        for val_name, val_num in keys.items():
            success = os.system(f'reg add "{path}" /v {val_name} /t REG_DWORD /d {val_num} /f /reg:64 >nul 2>&1')
            if success == 0:
                print(f"Success: {val_name} = {val_num} in {path}")

    print("3. Restarting ZoomIt...")
    os.system("start /B ZoomIt.exe")
    time.sleep(1.5)
    print("Ready!")

def trigger_action(action):
    hotkeys = {
        "zoom": "ctrl+shift+1",
        "draw": "ctrl+shift+2",
        "live": "ctrl+shift+3"
    }
    shortcut = hotkeys[action]
    print(f"Triggering: {shortcut}")
    keyboard.send(shortcut)

# --- GUI ---
root = tk.Tk()
root.title("The Final ZoomIt Test")
root.geometry("400x320")
root.attributes("-topmost", True)

tk.Button(root, text="🚀 שלב 1: הזרקת הגדרות סופיות", bg="red", fg="white", font=("Arial", 11, "bold"),
          command=lambda: root.after(10, setup_final_registry)).pack(pady=15, fill=tk.X, padx=20)

tk.Label(root, text="שלב 2: בדוק את הכלים:", font=("Arial", 10, "bold")).pack(pady=5)

tk.Button(root, text="🔍 זום (Ctrl+Shift+1)", bg="#2ECC71", fg="white", font=("Arial", 11), height=2,
          command=lambda: root.after(50, trigger_action, "zoom")).pack(pady=5, fill=tk.X, padx=30)

tk.Button(root, text="🖌️ ציור נקי (Ctrl+Shift+2)", bg="#F1C40F", font=("Arial", 11, "bold"), height=2,
          command=lambda: root.after(50, trigger_action, "draw")).pack(pady=5, fill=tk.X, padx=30)

tk.Button(root, text="🎥 זום חי (Ctrl+Shift+3)", bg="#E67E22", fg="white", font=("Arial", 11), height=2,
          command=lambda: root.after(50, trigger_action, "live")).pack(pady=5, fill=tk.X, padx=30)

tk.Label(root, text="* לחץ Esc כדי לצאת מהכלים", fg="gray", font=("Arial", 9)).pack(pady=10)

root.mainloop()