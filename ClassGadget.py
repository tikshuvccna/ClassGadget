import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
from PIL import Image, ImageTk, ImageGrab
import keyboard
import os
import shutil
import random
import sys
import datetime
import subprocess
from screeninfo import get_monitors
import pygame
import webbrowser
import winreg
import ctypes

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# --- תיקיות והגדרות ---
GIF_FOLDER = "gifs"; SOUND_FOLDER = "sounds"; RECORDINGS_FOLDER = "recordings"
DISPLAY_TIME_MS = 4000; FIREWORK_DISPLAY_TIME_MS = 1500
for folder in [GIF_FOLDER, SOUND_FOLDER, RECORDINGS_FOLDER]:
    if not os.path.exists(folder): os.makedirs(folder)

REGULAR_GIFS = {
    "כל הכבוד!": ("clap", "ctrl+alt+1"), 
    "שאלה מצוינת!": ("lightbulb", None), 
    "צחוק": ("laugh", "ctrl+alt+3"), 
    "תודה רבה": ("bow", "ctrl+alt+4"), 
    "ריכוז מירבי": ("focus", None), 
    "חשיבה...": ("thinking", None), 
    "עידוד (מתקשה)": ("support", None), 
    "תגמול (אלוף!)": ("champion", "ctrl+alt+8"), 
    "הפחדה": ("scary", None)
}
SPECIAL_EFFECTS_CONFIG = {
    "כפיים (עולות)": {"file": "clap_up", "hotkey": "ctrl+shift+1", "type": "move", "effect": "float_up"}, 
    "הפתעה (מחליק)": {"file": "wow", "hotkey": None, "type": "move", "effect": "slide_right"}, 
    "בלונים (עולים)": {"file": "balloons", "hotkey": None, "type": "move", "effect": "float_up"}, 
    "קונפטי (נופל)": {"file": "confetti", "hotkey": None, "type": "move", "effect": "drop_down"}, 
    "🎆 זיקוקים! 🎆": {"file": "firework", "hotkey": "ctrl+shift+5", "type": "fireworks"}
}

BGM_CONFIG = {"מוזיקה מפחידה": "bg_scary", "מוזיקה רגועה": "bg_calm", "מוזיקה שמחה": "bg_happy", "מוזיקה אנרגטית": "bg_energetic"}
SFX_CONFIG = {"מחיאות כפיים": "applause", "שעון מעורר": "alarm", "אוי אוי אוי": "oy_oy_oy", "פצצה": "bomb", "מסטיק מתפוצץ": "bubblegum", "תרנגול (סיום)": "chicken", "זיקוקים": "fireworks", "תופים (רולטה)": "drumroll", "הצלחה (טאדאם)": "tada"}

PROMPT_TEMPLATES = {
    "תמונה מסכמת": "צור תמונה מסכמת בנושא '{subject}'. התמונה צריכה להיות יפה, ברורה ומשקפת את הרעיונות המרכזיים.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה (כולל טקסטים בתוך התמונה במידה ויש) תהיה בעברית מדויקת, נכונה ויפה.",
    "אינפוגרפיקה מפורטת": "צור אינפוגרפיקה מפורטת וברורה בנושא '{subject}'. האינפוגרפיקה צריכה לסדר את המידע בצורה לוגית וויזואלית.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה.",
    "ויזואליזציה דינאמית": "בנה קוד לוויזואליזציה דינאמית בנושא '{subject}', הכוללת סימולציות, הנפשות ולחצנים אינטראקטיביים שמסבירים את הנושא.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: הממשק והטקסטים יהיו בעברית מדויקת, נכונה ויפה.",
    "חידון אינטראקטיבי": "צור קוד עבור חידון אינטראקטיבי בנושא '{subject}'. החידון יציג שאלה אחר שאלה עם משוב מיידי לכל תשובה, ומשוב מסכם בסוף. על החידון להיות מעוצב יפה ומסודר.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה.",
    "חדר בריחה": "צור קוד לחדר בריחה אינטראקטיבי בנושא '{subject}'. חדר הבריחה יכיל נרטיב מעניין, זמן מוגבל, מדד אנרגיה או ניקוד, קולות, רקע דינאמי המשתנה לפי השלב, צבעים חדים ומעניינים, ושאלות שהן חידות מעניינות ומיוחדות.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה והעלילה יהיו בעברית מדויקת, נכונה ויפה.",
    "כתיבת שיר": "כתוב שיר בנושא '{subject}'. השיר צריך להיות קליט וחינוכי.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה, תוך שמירה על חרוזים ומשקל הגיוני.",
    "סיכום ברמת תלמידים": "כתוב סיכום בנושא '{subject}' המותאם לרמת תלמידים. חלק את הסיכום לכותרות ברורות, בסגנון פשוט וברור. לכל חלק הצג קודם תקציר (נקודות מרכזיות) ולאחר מכן הרחבה. הצע בנוסף רעיונות לתמונות מלוות שניתן לשלב.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה.",
    "דף עבודה אינטראקטיבי": "צור קוד עבור דף עבודה אינטראקטיבי מקוון בנושא '{subject}'. הדף יכלול שדות מילוי, אפשרות לשליחה (Submit) שחוללת משוב אוטומטי ללומד, וכפתורים מובנים לצילום מסך של הציון והדפסה.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה.",
    "דף עבודה להדפסה": "הכן תוכן ועיצוב לדף עבודה מסודר ומקצועי המיועד להדפסה בנושא '{subject}'. הדף צריך להכיל מקום לכתיבה, שאלות מגוונות ואסתטיקה.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה תהיה בעברית מדויקת, נכונה ויפה.",
    "תסריט/קוד לקומיקס": "צור תסריט לקומיקס (או קוד המייצר קומיקס) בנושא '{subject}'. הקומיקס חייב להיות מיושר לימין (RTL) ולסכם את החומר הנלמד בצורה חמודה, חינוכית ומצחיקה.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: התוצאה והבועות טקסט יהיו בעברית מדויקת, נכונה ויפה.",
    "בניית אתר מודרני": "צור קוד (HTML/CSS/JS) לאתר אינטרנט מעוצב, מודרני ואינטראקטיבי בנושא '{subject}'. האתר צריך לכלול איורי SVG דינאמיים, אנימציות ממשק מתקדמות (כמו כפתורים שגדלים וקטנים במעבר עכבר - Hover effects), פריסה חדשנית וחוויית משתמש מושכת.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: כל הטקסטים והממשק יהיו בעברית מדויקת, נכונה ויפה, מיושרת לימין (RTL).",
    "יחידת לימוד שלמה": "צור קוד עבור יחידת לימוד שלמה ואינטראקטיבית בנושא '{subject}'. היחידה צריכה להכיל: 1. הסבר דינאמי וויזואלי על החומר. 2. סימולציה או הדגמה אינטראקטיבית. 3. קטע העמקה נוספת והגדרות. 4. חידון לבדיקת הידע עם משוב. הכל חייב להיות מעוצב בצורה מודרנית, נעימה ומותאמת פדגוגית ללמידה של תלמידים.\nסגנון רצוי: {style}\nפרטים נוספים: {details}\nהערה חשובה: כל התוכן יהיה בעברית מדויקת, נכונה ויפה, מיושר לימין (RTL)."
}

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, height=120)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")

class AnimatedGif(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.image = Image.open(path); self.frames = []
        try:
            while True: self.frames.append(ImageTk.PhotoImage(self.image.copy())); self.image.seek(len(self.frames))
        except EOFError: pass
        self.delay = self.image.info.get('duration', 100); self.idx = 0; self.after_id = None; self.play()
    def play(self):
        self.config(image=self.frames[self.idx]); self.idx = (self.idx + 1) % len(self.frames); self.after_id = self.after(self.delay, self.play)

class ClassGadgetApp:
    def __init__(self, root):
        self.root = root
        self.lang = "HE"
        pygame.mixer.init()
        
        self.master_vol_var = tk.DoubleVar(value=1.0); self.is_muted_var = tk.BooleanVar(value=False)
        self.opacity_var = tk.DoubleVar(value=1.0); self.always_on_top_var = tk.BooleanVar(value=False)
        self.music_vol_var = tk.DoubleVar(value=0.3); self.sfx_vol_var = tk.DoubleVar(value=0.7)
        self.messages_queue = []; self.current_msg_idx = 0; self.is_playing_messages = False
        self.custom_gifs = []; self.custom_sfx = []; self.polls_list = []
        
        self.gif_text_var = tk.StringVar(value="")
        self.gif_bg_var = tk.StringVar(value="#000000")
        self.gif_fg_var = tk.StringVar(value="#FFFFFF")
        
        self.audio_toggles = {}
        self.is_minimized = False
        
        self.normal_geometry = "840x700" 
        
        self.hide_window_var = tk.BooleanVar(value=False)

        self.setup_zoomit_registry()
        self.load_existing_custom_files()
        self.build_ui()

    def setup_zoomit_registry(self):
        if sys.platform == "win32":
            try:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Sysinternals\ZoomIt")
                winreg.SetValueEx(key, "EulaAccepted", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ToggleKey", 0, winreg.REG_DWORD, 0x07000077) # Ctrl+Alt+Shift+F8
                winreg.SetValueEx(key, "DrawKey", 0, winreg.REG_DWORD, 0x07000078)   # Ctrl+Alt+Shift+F9
                winreg.SetValueEx(key, "LiveZoomToggleKey", 0, winreg.REG_DWORD, 0x07000079) # Ctrl+Alt+Shift+F10
                winreg.SetValueEx(key, "RecordToggleKey", 0, winreg.REG_DWORD, 0x0700007A) # Ctrl+Alt+Shift+F11
                winreg.CloseKey(key)
            except Exception as e:
                print("Could not set ZoomIt registry keys:", e)

    def T(self, he, en): return he if self.lang == "HE" else en
    
    def switch_lang(self):
        self.lang = "EN" if self.lang == "HE" else "HE"
        for widget in self.root.winfo_children(): widget.destroy()
        self.build_ui()

    def toggle_minimize(self):
        if not self.is_minimized:
            self.normal_geometry = self.root.geometry()
            self.notebook.pack_forget()
            self.root.geometry("840x45") 
            self.btn_minimize.config(text="➕ הרחב", bg="#2ECC71", fg="black")
            self.is_minimized = True
        else:
            self.root.geometry(self.normal_geometry)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            self.btn_minimize.config(text="➖ כווץ", bg="#E74C3C", fg="white")
            self.is_minimized = False

    def toggle_window_visibility(self):
        if sys.platform == "win32":
            try:
                hwnd = int(self.root.wm_frame(), 16)
                if self.hide_window_var.get():
                    res = ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 17) 
                    if res == 0: ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 1) 
                else:
                    ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0) 
            except Exception as e:
                pass

    def build_ui(self):
        self.root.title(self.T("ClassGadget - אולפן מתקדם v18.0", "ClassGadget - Advanced Studio v18.0"))
        self.root.geometry(self.normal_geometry); self.root.attributes("-topmost", self.always_on_top_var.get()) 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        style = ttk.Style(); style.theme_use('clam')
        style.configure("TButton", font=("Arial", 10), padding=5); style.configure("Small.TButton", font=("Arial", 9, "bold"), padding=2)
        style.configure("Stop.TButton", font=("Arial", 11, "bold"), foreground="red")

        bar = tk.Frame(self.root, bg="#333333", pady=8, padx=10); bar.pack(fill=tk.X)
        
        self.btn_minimize = tk.Button(bar, text="➖ כווץ", bg="#E74C3C", fg="white", font=("Arial", 10, "bold"), bd=0, command=self.toggle_minimize)
        self.btn_minimize.pack(side=tk.RIGHT, padx=5)
        
        tk.Button(bar, text="🌐 HE/EN", bg="#555", fg="white", bd=0, command=self.switch_lang).pack(side=tk.RIGHT, padx=5)
        
        tk.Checkbutton(bar, text="👻 הסתר מזום (נסיוני)", variable=self.hide_window_var, bg="#333333", fg="#F1C40F", selectcolor="black", font=("Arial", 9, "bold"), command=self.toggle_window_visibility).pack(side=tk.RIGHT, padx=10)
        tk.Checkbutton(bar, text=self.T("📌 נעוץ", "📌 Pin"), variable=self.always_on_top_var, bg="#333333", fg="white", selectcolor="black", command=self.update_topmost).pack(side=tk.RIGHT, padx=5)
        
        tk.Label(bar, text=self.T("שקיפות:", "Opacity:"), bg="#333333", fg="white").pack(side=tk.RIGHT, padx=(5,2))
        ttk.Scale(bar, from_=0.2, to=1.0, variable=self.opacity_var, command=self.update_opacity).pack(side=tk.RIGHT)
        tk.Checkbutton(bar, text=self.T("🔇 השתק הכל", "🔇 Mute All"), variable=self.is_muted_var, bg="#333333", fg="red", selectcolor="black", command=self.update_global_volume).pack(side=tk.LEFT, padx=5)
        ttk.Scale(bar, from_=0.0, to=1.0, variable=self.master_vol_var, command=self.update_global_volume).pack(side=tk.LEFT)
        tk.Label(bar, text=self.T("🔊 מאסטר:", "🔊 Master:"), bg="#333333", fg="white").pack(side=tk.LEFT, padx=(5,2))

        top_frame = tk.Frame(self.root, bg="#e6f2ff", pady=5); top_frame.pack(fill=tk.X)
        self.monitors = get_monitors(); self.monitor_names = [f"{self.T('מסך', 'Screen')} {i+1} ({m.width}x{m.height})" for i, m in enumerate(self.monitors)]
        self.selected_monitor_var = tk.StringVar(self.root); self.selected_monitor_var.set(self.monitor_names[0])
        ttk.OptionMenu(top_frame, self.selected_monitor_var, self.monitor_names[0], *self.monitor_names).pack(side=tk.RIGHT)
        tk.Label(top_frame, text=self.T("בחר מסך הצגה:", "Select Display:"), font=("Arial", 11, "bold"), bg="#e6f2ff").pack(side=tk.RIGHT, padx=10)

        self.notebook = ttk.Notebook(self.root); self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.tab_regular = ttk.Frame(self.notebook); self.tab_effects = ttk.Frame(self.notebook)
        self.tab_sounds = ttk.Frame(self.notebook); self.tab_tools = ttk.Frame(self.notebook)
        self.tab_polls = ttk.Frame(self.notebook); self.tab_games = ttk.Frame(self.notebook)
        self.tab_prompts = ttk.Frame(self.notebook); self.tab_screen = ttk.Frame(self.notebook) 
        self.tab_fullscreen = ttk.Frame(self.notebook); self.tab_about = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_regular, text=self.T("🎭 גיפים", "🎭 GIFs"))
        self.notebook.add(self.tab_effects, text=self.T("✨ אפקטים", "✨ Effects"))
        self.notebook.add(self.tab_screen, text=self.T("🖌️ כלי מסך וזום", "🖌️ Screen Tools"))
        self.notebook.add(self.tab_sounds, text=self.T("🔊 צלילים", "🔊 Sounds"))
        self.notebook.add(self.tab_tools, text=self.T("📰 מבזקים ורולטה", "📰 Ticker & Roulette"))
        self.notebook.add(self.tab_polls, text=self.T("📊 סקרים", "📊 Polls"))
        self.notebook.add(self.tab_games, text=self.T("🎮 משחקים", "🎮 Games"))
        self.notebook.add(self.tab_prompts, text=self.T("🤖 פרומפטים", "🤖 Prompts"))
        self.notebook.add(self.tab_fullscreen, text=self.T("📺 מסכי המתנה", "📺 Screensavers"))
        self.notebook.add(self.tab_about, text=self.T("ℹ️ אודות", "ℹ️ About"))

        self.build_shared_gif_config()
        self.build_regular_tab(); self.build_effects_tab(); self.build_screen_tools_tab()
        self.build_sounds_tab(); self.build_tools_tab(); self.build_polls_tab(); self.build_games_tab()
        self.build_prompts_tab(); self.build_fullscreen_tab(); self.build_about_tab()

        self.popup = None; self.firework_popups = []
        self.msg_popup = None; self.msg_job = None; self.roulette_popup = None
        self.fs_popup = None; self.fs_timer_job = None; self.fs_anim_jobs = []
        self.hangman_popup = None; self.scramble_popup = None; self.poll_popup = None

    def on_closing(self):
        try: pygame.mixer.quit()
        except: pass
        # סגירת ZoomIt כדי שלא יישאר פעיל ברקע
        if sys.platform == "win32":
            os.system("taskkill /f /im ZoomIt.exe >nul 2>&1")
            os.system("taskkill /f /im ZoomIt64.exe >nul 2>&1")
        self.root.destroy()
        sys.exit(0)

    def load_existing_custom_files(self):
        known_gifs = set([v[0]+".gif" for v in REGULAR_GIFS.values()] + [v[0]+f"{i}.gif" for v in REGULAR_GIFS.values() for i in range(1,7)] + [v['file']+".gif" for v in SPECIAL_EFFECTS_CONFIG.values()] + [v['file']+f"{i}.gif" for v in SPECIAL_EFFECTS_CONFIG.values() for i in range(1,7)])
        if os.path.exists(GIF_FOLDER):
            for f in os.listdir(GIF_FOLDER):
                if f.lower().endswith(('.gif','.png','.jpg')) and f not in known_gifs and "start" not in f and "coffee" not in f: self.custom_gifs.append(f)

    def update_topmost(self): self.root.attributes("-topmost", self.always_on_top_var.get())
    def update_opacity(self, val): self.root.attributes("-alpha", float(val))
    def update_global_volume(self, *args): pygame.mixer.music.set_volume(self.music_vol_var.get() * (0.0 if self.is_muted_var.get() else self.master_vol_var.get()))
    def get_actual_sfx_volume(self): return 0.0 if self.is_muted_var.get() else self.sfx_vol_var.get() * self.master_vol_var.get()

    def add_custom_media(self, m_type):
        fp = filedialog.askopenfilename(title=self.T("בחר קובץ", "Select File"))
        if fp:
            fn = os.path.basename(fp)
            if m_type == "gif": shutil.copy(fp, os.path.join(GIF_FOLDER, fn)); self.custom_gifs.append(fn); self.refresh_custom_gifs_ui()
            else: shutil.copy(fp, os.path.join(SOUND_FOLDER, fn)); self.custom_sfx.append(fn); self.refresh_custom_sfx_ui()

    def delete_custom_media(self, fn, m_type):
        if messagebox.askyesno(self.T("מחיקה", "Delete"), f"{self.T('למחוק את', 'Delete')} {fn}?"):
            if m_type == 'gif':
                p = os.path.join(GIF_FOLDER, fn)
                if os.path.exists(p): os.remove(p)
                self.custom_gifs.remove(fn); self.refresh_custom_gifs_ui()
            elif m_type == 'sfx':
                p = os.path.join(SOUND_FOLDER, fn)
                if os.path.exists(p): os.remove(p)
                self.custom_sfx.remove(fn); self.refresh_custom_sfx_ui()

    def get_sound_toggle(self, key):
        if key not in self.audio_toggles:
            self.audio_toggles[key] = tk.BooleanVar(value=True)
        return self.audio_toggles[key]

    def build_shared_gif_config(self):
        for tab in [self.tab_regular, self.tab_effects]:
            f = tk.Frame(tab, bg="#f0f0f0", pady=5, padx=5, relief="ridge", bd=2)
            f.pack(fill=tk.X, pady=(0, 10))
            tk.Label(f, text="טקסט מלווה לגיף/אפקט (לא חובה):", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
            ttk.Entry(f, textvariable=self.gif_text_var, width=25).pack(side=tk.RIGHT, padx=5)
            
            ttk.Button(f, text="🗑️ נקה", command=lambda: self.gif_text_var.set("")).pack(side=tk.RIGHT, padx=5)
            
            btn_bg = tk.Button(f, text="רקע", bg=self.gif_bg_var.get(), fg="white")
            btn_bg.config(command=lambda v=self.gif_bg_var, b=btn_bg: self.pick_color(v, b))
            btn_bg.pack(side=tk.RIGHT, padx=2)
            
            btn_fg = tk.Button(f, text="טקסט", bg=self.gif_fg_var.get(), fg="black")
            btn_fg.config(command=lambda v=self.gif_fg_var, b=btn_fg: self.pick_color(v, b))
            btn_fg.pack(side=tk.RIGHT, padx=2)

    def pick_color(self, var, btn):
        color = colorchooser.askcolor(initialcolor=var.get())[1]
        if color: 
            var.set(color)
            btn.config(bg=color)

    # --- גיפים ---
    def build_regular_tab(self):
        ttk.Button(self.tab_regular, text=self.T("➕ העלה תמונה/GIF", "➕ Upload GIF"), command=lambda: self.add_custom_media("gif")).pack(pady=5)
        for name, (pref, hk) in REGULAR_GIFS.items():
            f = tk.Frame(self.tab_regular); f.pack(fill=tk.X, pady=2, padx=10)
            
            hk_text = f" ({hk})" if hk else ""
            tk.Label(f, text=f"{name}{hk_text}", width=25, anchor="e").pack(side=tk.RIGHT, padx=5)
            
            snd_var = self.get_sound_toggle(pref)
            tk.Checkbutton(f, text="🔊", variable=snd_var, font=("Segoe UI Emoji", 10)).pack(side=tk.RIGHT, padx=5)
            
            for i in range(1, 7): 
                fn = f"{pref if i==1 else pref+str(i-1)}.gif"
                ttk.Button(f, text=str(i), width=3, style="Small.TButton", command=lambda f_n=fn, p=pref: self.trigger_gif(f_n, "center", self.get_sound_toggle(p).get())).pack(side=tk.RIGHT, padx=1)
            
            ttk.Button(f, text="🎲", width=4, command=lambda p=pref: self.trigger_random_gif(p, "center", self.get_sound_toggle(p).get())).pack(side=tk.RIGHT, padx=5)
            
            if hk:
                keyboard.add_hotkey(hk, lambda p=pref: self.root.after(0, self.trigger_gif, f"{p}.gif", "center", self.get_sound_toggle(p).get()))
            
        self.custom_gifs_frame = tk.LabelFrame(self.tab_regular, text=self.T("הוספו אישית", "Custom Added"), font=("Arial", 10, "bold")); self.custom_gifs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.gifs_scroll = ScrollableFrame(self.custom_gifs_frame); self.gifs_scroll.pack(fill=tk.BOTH, expand=True)
        self.refresh_custom_gifs_ui()

    def refresh_custom_gifs_ui(self):
        for w in self.gifs_scroll.scrollable_frame.winfo_children(): w.destroy()
        for fn in self.custom_gifs:
            f = tk.Frame(self.gifs_scroll.scrollable_frame); f.pack(fill=tk.X, pady=2, padx=5)
            tk.Label(f, text=fn, anchor="e", width=20).pack(side=tk.RIGHT, padx=5)
            snd_var = self.get_sound_toggle(fn)
            tk.Checkbutton(f, text="🔊", variable=snd_var, font=("Segoe UI Emoji", 10)).pack(side=tk.RIGHT, padx=5)
            tk.Button(f, text="🗑️", bg="#ffcccc", bd=0, command=lambda n=fn: self.delete_custom_media(n, 'gif')).pack(side=tk.LEFT, padx=5)
            ttk.Button(f, text=self.T("הפעל", "Play"), command=lambda n=fn: self.trigger_gif(n, "center", self.get_sound_toggle(n).get())).pack(side=tk.RIGHT)

    def build_effects_tab(self):
        ttk.Label(self.tab_effects, text=self.T("אפקטים מיוחדים וזיקוקים:", "Special Effects:")).pack(pady=5)
        for name, conf in SPECIAL_EFFECTS_CONFIG.items():
            f = tk.Frame(self.tab_effects); f.pack(fill=tk.X, pady=5, padx=10)
            
            hk = conf['hotkey']
            hk_text = f" ({hk})" if hk else ""
            tk.Label(f, text=f"{name}{hk_text}", width=25, anchor="e").pack(side=tk.RIGHT, padx=5)
            
            snd_var = self.get_sound_toggle(conf['file'])
            tk.Checkbutton(f, text="🔊", variable=snd_var, font=("Segoe UI Emoji", 10)).pack(side=tk.RIGHT, padx=5)

            for i in range(1, 7):
                fn = f"{conf['file'] if i==1 else conf['file']+str(i-1)}.gif"
                if conf['type'] == "move":
                    cmd = lambda f_n=fn, e=conf['effect'], p=conf['file']: self.trigger_gif(f_n, e, self.get_sound_toggle(p).get())
                else:
                    cmd = lambda f_n=fn, p=conf['file']: self.trigger_fireworks(f_n, self.get_sound_toggle(p).get())
                ttk.Button(f, text=str(i), width=3, style="Small.TButton", command=cmd).pack(side=tk.RIGHT, padx=1)
                
            if conf['type'] == "move":
                cmd_rand = lambda p=conf['file'], e=conf['effect']: self.trigger_random_gif(p, e, self.get_sound_toggle(p).get())
            else:
                cmd_rand = lambda p=conf['file']: self.trigger_random_fireworks(p, self.get_sound_toggle(p).get())
            ttk.Button(f, text="🎲", width=4, command=cmd_rand).pack(side=tk.RIGHT, padx=5)
            
            if hk:
                if conf['type'] == "move":
                    keyboard.add_hotkey(hk, lambda f_n=f"{conf['file']}.gif", e=conf['effect'], p=conf['file']: self.root.after(0, self.trigger_gif, f_n, e, self.get_sound_toggle(p).get()))
                else:
                    keyboard.add_hotkey(hk, lambda f_n=f"{conf['file']}.gif", p=conf['file']: self.root.after(0, self.trigger_fireworks, f_n, self.get_sound_toggle(p).get()))


    # --- כלי מסך וזום ---
    def build_screen_tools_tab(self):
        ss_frame = tk.LabelFrame(self.tab_screen, text="📸 צילום והקלטת מסך", font=("Arial", 12, "bold"), pady=10, padx=10)
        ss_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(ss_frame, text="הקבצים יישמרו אוטומטית בתיקיית recordings/", font=("Arial", 11)).pack(pady=5)
        
        btn_f = tk.Frame(ss_frame); btn_f.pack()
        tk.Button(btn_f, text="צילום מסך מלא", bg="#3498DB", fg="white", font=("Arial", 11, "bold"), width=15, command=self.take_full_screenshot).pack(side=tk.RIGHT, padx=10, pady=5)
        tk.Button(btn_f, text="חיתוך אזור (מסומן)", bg="#9B59B6", fg="white", font=("Arial", 11, "bold"), width=15, command=self.start_custom_snip).pack(side=tk.RIGHT, padx=10, pady=5)
        tk.Button(btn_f, text="🔴 הקלטת וידאו (נסיוני)", bg="#E74C3C", fg="white", font=("Arial", 11, "bold"), width=22, command=lambda: self.run_zoomit('record')).pack(side=tk.RIGHT, padx=10, pady=5)

        zi_frame = tk.LabelFrame(self.tab_screen, text="🔍 כלי ציור וזום (מבוסס ZoomIt)", font=("Arial", 12, "bold"), pady=10, padx=10)
        zi_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        if not os.path.exists("ZoomIt.exe"):
            tk.Label(zi_frame, text="⚠️ הקובץ ZoomIt.exe חסר בתיקייה!\nהורידו ושימו אותו כאן כדי להשתמש בכלים.", fg="red", font=("Arial", 11, "bold")).pack(pady=5)
        else:
            z_ctrl = tk.Frame(zi_frame); z_ctrl.pack(pady=5)
            tk.Label(z_ctrl, text="רמת זום (תחול בהפעלה הבאה):").pack(side=tk.RIGHT, padx=5)
            self.zoom_level_var = tk.StringVar(value="2x (מומלץ)")
            cb_zoom = ttk.Combobox(z_ctrl, textvariable=self.zoom_level_var, values=["1.5x", "2x (מומלץ)", "3x", "4x"], width=12, state="readonly")
            cb_zoom.pack(side=tk.RIGHT, padx=5)
            cb_zoom.bind("<<ComboboxSelected>>", self.set_zoomit_level)
            
            acts = tk.Frame(zi_frame); acts.pack(pady=10)
            
            tk.Button(acts, text="✖️ יציאה / בטל", font=("Arial", 11, "bold"), bg="#E74C3C", fg="white", width=12, command=self.cancel_zoomit).grid(row=0, column=0, padx=5)
            tk.Label(acts, text="(Esc)", font=("Arial", 9), fg="gray").grid(row=1, column=0)

            tk.Button(acts, text="🎥 זום חי", font=("Arial", 11, "bold"), bg="#E67E22", width=12, command=lambda: self.run_zoomit('live')).grid(row=0, column=2, padx=5)
            tk.Label(acts, text="(Ctrl+4)", font=("Arial", 9), fg="gray").grid(row=1, column=2)

            tk.Button(acts, text="🖌️ מצב ציור", font=("Arial", 11, "bold"), bg="#F1C40F", width=12, command=lambda: self.run_zoomit('draw')).grid(row=0, column=3, padx=5)
            tk.Label(acts, text="(Ctrl+2)", font=("Arial", 9), fg="gray").grid(row=1, column=3)

            tk.Button(acts, text="🔍 הפעל זום", font=("Arial", 11, "bold"), bg="#2ECC71", width=12, command=lambda: self.run_zoomit('zoom')).grid(row=0, column=4, padx=5)
            tk.Label(acts, text="(Ctrl+1)", font=("Arial", 9), fg="gray").grid(row=1, column=4)

            tk.Label(zi_frame, text="🔴 ליציאה ממצב זום או ציור – לחצו על מקש ה- ESC במקלדת! 🔴", font=("Arial", 14, "bold"), fg="#C0392B", bg="#FADBD8", pady=5).pack(fill=tk.X, pady=10)
            
            tk.Label(zi_frame, text="קיצורי דרך למצב ציור:", font=("Arial", 12, "bold", "underline")).pack(pady=5)
            shortcuts = [
                ("מלבן:", "לחיצה ארוכה על Ctrl + גרירת עכבר"),
                ("קו ישר:", "לחיצה ארוכה על Shift + גרירת עכבר"),
                ("חץ:", "לחיצה ארוכה על Ctrl + Shift + גרירת עכבר"),
                ("עיגול:", "לחיצה ארוכה על Tab + גרירת עכבר"),
                ("מסך שחור / לבן:", "לחיצה על האות K לשחור, או W ללבן"),
                ("כתיבת טקסט:", "לחיצה על האות T ולאחר מכן הקלדה"),
                ("מחק הכל:", "לחיצה על האות E")
            ]
            for title, desc in shortcuts:
                rf = tk.Frame(zi_frame); rf.pack(fill=tk.X)
                tk.Label(rf, text="\u202B" + desc + "\u202C", font=("Arial", 11)).pack(side=tk.RIGHT)
                tk.Label(rf, text="\u202B" + title + "\u202C", font=("Arial", 11, "bold")).pack(side=tk.RIGHT, padx=(0, 10))

    def take_full_screenshot(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(RECORDINGS_FOLDER, f"Screenshot_{timestamp}.png")
            img = ImageGrab.grab(all_screens=True)
            img.save(filename)
            self.play_sound("applause")
            self.show_quiet_notification(f"המסך צולם ונשמר בתיקייה!")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בצילום המסך:\n{e}")

    def start_custom_snip(self):
        self.snip_win = tk.Toplevel(self.root)
        self.snip_win.attributes("-fullscreen", True)
        self.snip_win.attributes("-alpha", 0.3)
        self.snip_win.attributes("-topmost", True)
        self.snip_win.config(cursor="crosshair", bg="black")
        
        self.snip_canvas = tk.Canvas(self.snip_win, cursor="crosshair", bg="black")
        self.snip_canvas.pack(fill="both", expand=True)
        
        self.snip_start_x = None
        self.snip_start_y = None
        self.snip_rect = None

        self.snip_canvas.bind("<ButtonPress-1>", self.on_snip_press)
        self.snip_canvas.bind("<B1-Motion>", self.on_snip_drag)
        self.snip_canvas.bind("<ButtonRelease-1>", self.on_snip_release)
        self.snip_win.bind("<Escape>", lambda e: self.snip_win.destroy())
        
        self.snip_win.focus_force()

    def on_snip_press(self, event):
        self.snip_start_x = event.x
        self.snip_start_y = event.y
        self.snip_rect = self.snip_canvas.create_rectangle(self.snip_start_x, self.snip_start_y, 1, 1, outline='red', width=2, fill="white")

    def on_snip_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.snip_canvas.coords(self.snip_rect, self.snip_start_x, self.snip_start_y, cur_x, cur_y)

    def on_snip_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.snip_win.destroy()
        
        x1 = min(self.snip_start_x, end_x)
        y1 = min(self.snip_start_y, end_y)
        x2 = max(self.snip_start_x, end_x)
        y2 = max(self.snip_start_y, end_y)
        
        if x2 - x1 > 10 and y2 - y1 > 10:
            self.root.after(100, lambda: self.save_snip(x1, y1, x2, y2))

    def save_snip(self, x1, y1, x2, y2):
        try:
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = os.path.join(RECORDINGS_FOLDER, f"Snip_{timestamp}.png")
            img.save(filename)
            self.play_sound("applause")
            self.show_quiet_notification("החיתוך נשמר בתיקייה בהצלחה!")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בחיתוך:\n{e}")

    def set_zoomit_level(self, event=None):
        val = self.zoom_level_var.get()
        level_map = {"1.5x": 1, "2x (מומלץ)": 2, "3x": 3, "4x": 4}
        lvl = level_map.get(val, 2)
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Sysinternals\ZoomIt")
            winreg.SetValueEx(key, "ZoomLevel", 0, winreg.REG_DWORD, lvl)
            winreg.CloseKey(key)
        except:
            pass

    def ensure_zoomit_running(self):
        output = subprocess.getoutput("tasklist")
        if "ZoomIt.exe" not in output and "ZoomIt64.exe" not in output:
            os.system("start /B ZoomIt.exe")
            return True
        return False

    def run_zoomit(self, mode):
        if not os.path.exists("ZoomIt.exe"): return
        
        was_just_started = self.ensure_zoomit_running()
        
        hotkeys = {
            "zoom": "ctrl+alt+shift+f8",
            "draw": "ctrl+alt+shift+f9",
            "live": "ctrl+alt+shift+f10",
            "record": "ctrl+alt+shift+f11"
        }
        if mode == "record":
            self.show_quiet_notification("הקלטת וידאו מופעלת/נעצרת. בסיום תתבקש לבחור היכן לשמור.", 4000)
            
        delay = 1000 if was_just_started else 100
        self.root.after(delay, lambda: keyboard.send(hotkeys[mode]))

    def cancel_zoomit(self):
        keyboard.send("escape")
        keyboard.send("ctrl+alt+shift+f10")

    def build_sounds_tab(self):
        ttk.Button(self.tab_sounds, text=self.T("➕ העלה סאונד", "➕ Upload Sound"), command=lambda: self.add_custom_media("sfx")).pack(pady=5)
        cf = tk.Frame(self.tab_sounds); cf.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(cf, text=self.T("⏹️ עצור הכל", "Stop All"), style="Stop.TButton", command=self.stop_all_audio).pack(side=tk.RIGHT, padx=5)
        ttk.Button(cf, text=self.T("⏸️ השהה", "Pause"), command=self.pause_audio).pack(side=tk.RIGHT, padx=5)
        ttk.Button(cf, text=self.T("▶️ המשך", "Resume"), command=self.resume_audio).pack(side=tk.RIGHT, padx=5)
        vf = tk.Frame(self.tab_sounds); vf.pack(fill=tk.X, padx=10, pady=5)
        ttk.Scale(vf, from_=0.0, to=1.0, variable=self.music_vol_var, command=self.update_global_volume).pack(side=tk.RIGHT, padx=5); tk.Label(vf, text="מוזיקה:").pack(side=tk.RIGHT)
        ttk.Scale(vf, from_=0.0, to=1.0, variable=self.sfx_vol_var).pack(side=tk.RIGHT, padx=(10,5)); tk.Label(vf, text="אפקטים:").pack(side=tk.RIGHT)
        cols = tk.Frame(self.tab_sounds); cols.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        f_bgm = tk.LabelFrame(cols, text=self.T("🎵 רקע", "🎵 BGM")); f_bgm.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=2)
        for name, base in BGM_CONFIG.items():
            f = tk.Frame(f_bgm); f.pack(fill=tk.X, pady=2); tk.Label(f, text=name, anchor="e").pack(side=tk.TOP, fill=tk.X)
            for i in range(1, 7): ttk.Button(f, text=str(i), width=2, style="Small.TButton", command=lambda b=f"{base if i==1 else base+str(i-1)}": self.play_bgm(b)).pack(side=tk.RIGHT)
        f_sfx = tk.LabelFrame(cols, text=self.T("🎬 אפקטים", "🎬 SFX")); f_sfx.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        for name, base in SFX_CONFIG.items():
            f = tk.Frame(f_sfx); f.pack(fill=tk.X, pady=2); tk.Label(f, text=name, anchor="e").pack(side=tk.TOP, fill=tk.X)
            for i in range(1, 7): ttk.Button(f, text=str(i), width=2, style="Small.TButton", command=lambda b=f"{base if i==1 else base+str(i-1)}": self.play_sound(b)).pack(side=tk.RIGHT)
        self.custom_sfx_frame = tk.LabelFrame(cols, text=self.T("הוספו אישית", "Custom")); self.custom_sfx_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=2, pady=5)
        self.sfx_scroll = ScrollableFrame(self.custom_sfx_frame); self.sfx_scroll.pack(fill=tk.BOTH, expand=True)
        self.refresh_custom_sfx_ui()

    def refresh_custom_sfx_ui(self):
        for w in self.sfx_scroll.scrollable_frame.winfo_children(): w.destroy()
        for fn in self.custom_sfx:
            f = tk.Frame(self.sfx_scroll.scrollable_frame); f.pack(fill=tk.X, pady=2)
            tk.Label(f, text=fn, anchor="e", width=15).pack(side=tk.RIGHT)
            tk.Button(f, text="🗑️", bg="#ffcccc", bd=0, command=lambda n=fn: self.delete_custom_media(n, 'sfx')).pack(side=tk.LEFT, padx=5)
            ttk.Button(f, text="SFX", style="Small.TButton", command=lambda n=fn: self.play_sound(n.split('.')[0])).pack(side=tk.RIGHT, padx=2)
            ttk.Button(f, text="BGM", style="Small.TButton", command=lambda n=fn: self.play_bgm(n.split('.')[0])).pack(side=tk.RIGHT, padx=2)

    def build_tools_tab(self):
        f_roul = tk.LabelFrame(self.tab_tools, text=self.T("🎡 גלגל שמות", "🎡 Roulette"), font=("Arial", 11, "bold")); f_roul.pack(fill=tk.X, padx=10, pady=5)
        self.roulette_names_var = tk.StringVar(value="אבי, דנה, רון, שירה, משה"); ttk.Entry(f_roul, textvariable=self.roulette_names_var, font=("Arial", 12)).pack(fill=tk.X, padx=10, pady=5)
        ctrl_r = tk.Frame(f_roul); ctrl_r.pack()
        tk.Label(ctrl_r, text=self.T("צבע שם:", "Name Color:")).pack(side=tk.RIGHT, padx=5)
        self.r_col_var = tk.StringVar(value="#FFD700")
        r_col_btn = tk.Button(ctrl_r, text="  ", bg=self.r_col_var.get(), width=4, relief="ridge", command=lambda: self.pick_color(self.r_col_var, r_col_btn)); r_col_btn.pack(side=tk.RIGHT, padx=5)
        ttk.Button(ctrl_r, text=self.T("🎲 הגרל תלמיד!", "🎲 Spin!"), command=self.start_roulette).pack(side=tk.RIGHT, padx=10)

        f_msg = tk.LabelFrame(self.tab_tools, text=self.T("📰 מבזק חדשות מתקדם", "📰 Advanced Ticker"), font=("Arial", 11, "bold")); f_msg.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        form = tk.Frame(f_msg); form.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(form, text=self.T("ההודעה:", "Message:")).grid(row=0, column=3, sticky="e", pady=2)
        self.msg_text_var = tk.StringVar(); ttk.Entry(form, textvariable=self.msg_text_var, width=50).grid(row=0, column=0, columnspan=3, pady=2, sticky="e")
        tk.Label(form, text=self.T("סגנון:", "Style:")).grid(row=1, column=3, sticky="e", pady=2)
        self.msg_type_var = tk.StringVar(value="נגלל"); ttk.Combobox(form, textvariable=self.msg_type_var, values=["נגלל", "סטטי", "קופץ"], width=10, state="readonly").grid(row=1, column=2, sticky="e")
        tk.Label(form, text=self.T("מיקום:", "Pos:")).grid(row=1, column=1, sticky="e")
        self.msg_loc_var = tk.StringVar(value="למטה"); ttk.Combobox(form, textvariable=self.msg_loc_var, values=["למעלה", "מרכז", "למטה"], width=10, state="readonly").grid(row=1, column=0, sticky="e")
        tk.Label(form, text=self.T("זמן להצגה (שניות):", "Duration (sec):")).grid(row=2, column=3, sticky="e", pady=2)
        self.msg_time_var = tk.StringVar(value="10"); ttk.Entry(form, textvariable=self.msg_time_var, width=5).grid(row=2, column=2, sticky="e")
        tk.Label(form, text=self.T("גודל גופן:", "Font Size:")).grid(row=2, column=1, sticky="e")
        self.msg_size_var = tk.StringVar(value="60"); ttk.Combobox(form, textvariable=self.msg_size_var, values=["20","36","50","60","80","120","150","200","300"], width=8).grid(row=2, column=0, sticky="e")

        color_frame = tk.Frame(f_msg); color_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(color_frame, text=self.T("צבעי טקסט מתחלפים:", "Text Colors:")).pack(side=tk.RIGHT, padx=2)
        self.c1 = tk.StringVar(value="#FFD700"); self.c2 = tk.StringVar(value="#FFFFFF"); self.c3 = tk.StringVar(value="#FF4500")
        b1=tk.Button(color_frame, bg=self.c1.get(), width=2, relief="ridge"); b1.config(command=lambda: self.pick_color(self.c1, b1)); b1.pack(side=tk.RIGHT, padx=1)
        b2=tk.Button(color_frame, bg=self.c2.get(), width=2, relief="ridge"); b2.config(command=lambda: self.pick_color(self.c2, b2)); b2.pack(side=tk.RIGHT, padx=1)
        b3=tk.Button(color_frame, bg=self.c3.get(), width=2, relief="ridge"); b3.config(command=lambda: self.pick_color(self.c3, b3)); b3.pack(side=tk.RIGHT, padx=1)
        tk.Label(color_frame, text="  |  "+self.T("צבע רקע:", "Bg Color:")).pack(side=tk.RIGHT, padx=2)
        self.bg_c = tk.StringVar(value="#000000")
        bbg=tk.Button(color_frame, bg=self.bg_c.get(), width=2, relief="ridge"); bbg.config(command=lambda: self.pick_color(self.bg_c, bbg)); bbg.pack(side=tk.RIGHT, padx=1)

        opt_frame = tk.Frame(f_msg); opt_frame.pack(fill=tk.X, padx=5, pady=2)
        self.msg_loop_var = tk.BooleanVar(value=False); tk.Checkbutton(opt_frame, text=self.T("לולאה אינסופית (לא ייעלם)", "Infinite Loop"), variable=self.msg_loop_var).pack(side=tk.RIGHT)
        self.msg_full_w_var = tk.BooleanVar(value=True); tk.Checkbutton(opt_frame, text=self.T("רקע אטום לכל רוחב המסך", "Full Width Solid Bg"), variable=self.msg_full_w_var).pack(side=tk.RIGHT, padx=10)
        ttk.Button(opt_frame, text="➕ " + self.T("הוסף לרשימה", "Add"), command=self.add_msg).pack(side=tk.LEFT)

        self.msg_listbox = tk.Listbox(f_msg, height=4, font=("Arial", 10), justify="right"); self.msg_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        bf = tk.Frame(f_msg); bf.pack(fill=tk.X, pady=5)
        ttk.Button(bf, text="🗑️ נקה הכל", command=self.clear_msgs).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bf, text="❌ הסר נבחר", command=self.remove_selected_msg).pack(side=tk.RIGHT, padx=2)
        ttk.Button(bf, text="⏹️ עצור", command=self.stop_msgs).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="▶️ הפעל טיקר", command=self.play_msgs).pack(side=tk.LEFT, padx=5)

    def add_msg(self):
        t = self.msg_text_var.get().strip(); 
        if not t: return
        m = {"text": t, "type": self.msg_type_var.get(), "loc": self.msg_loc_var.get(), "time": int(self.msg_time_var.get() or 10), "size": int(self.msg_size_var.get()), "loop": self.msg_loop_var.get(), "colors": [self.c1.get(), self.c2.get(), self.c3.get()], "bg": self.bg_c.get(), "full_width": self.msg_full_w_var.get()}
        self.messages_queue.append(m); self.msg_listbox.insert(tk.END, f"[{m['type']}] {t}"); self.msg_text_var.set("")
    
    def remove_selected_msg(self):
        sel = self.msg_listbox.curselection()
        if sel: idx = sel[0]; self.msg_listbox.delete(idx); self.messages_queue.pop(idx)
        
    def clear_msgs(self): self.messages_queue.clear(); self.msg_listbox.delete(0, tk.END)
    def stop_msgs(self):
        self.is_playing_messages = False
        if self.msg_popup and self.msg_popup.winfo_exists():
            if self.msg_job: self.root.after_cancel(self.msg_job)
            self.msg_popup.destroy()
            
    def play_msgs(self):
        if not self.messages_queue: return
        self.stop_msgs(); self.is_playing_messages = True; self.current_msg_idx = 0; self.show_msg()
        
    def show_msg(self):
        if not self.is_playing_messages: return
        if self.current_msg_idx >= len(self.messages_queue):
            if any(m["loop"] for m in self.messages_queue): self.current_msg_idx = 0
            else: self.stop_msgs(); return
            
        m = self.messages_queue[self.current_msg_idx]
        self.msg_popup = tk.Toplevel(self.root); self.msg_popup.overrideredirect(True); self.msg_popup.attributes("-topmost", True)
        
        bg_col = m["bg"]
        if m["full_width"]: self.msg_popup.config(bg=bg_col)
        else: self.msg_popup.attributes("-transparentcolor", "black"); self.msg_popup.config(bg="black"); bg_col = "black" if bg_col == "black" else bg_col
            
        target = self.get_target_monitor()
        self.msg_label = tk.Label(self.msg_popup, text=m["text"], font=("Arial", m["size"], "bold"), fg=m["colors"][0], bg=m["bg"])
        self.msg_label.pack(fill=tk.Y if m["full_width"] else tk.NONE); self.msg_popup.update_idletasks()
        
        w, h = self.msg_popup.winfo_width(), self.msg_popup.winfo_height()
        y = target.y + 50 if m["loc"] == "למעלה" else (target.y + (target.height/2) - (h/2) if m["loc"] == "מרכז" else target.y + target.height - h - 50)
        t_ms = m["time"] * 1000; self.color_idx = 0
        
        if m["type"] == "נגלל":
            win_w = target.width if m["full_width"] else target.width
            self.msg_popup.geometry(f'{win_w}x{h}+{target.x}+{int(y)}'); self.msg_x = target.width; self.msg_label.place(x=self.msg_x, y=0); self.anim_scroll(target.width, t_ms, m)
        elif m["type"] == "סטטי":
            win_w = target.width if m["full_width"] else w
            x_pos = target.x if m["full_width"] else target.x + (target.width/2) - (w/2)
            self.msg_popup.geometry(f'{win_w}x{h}+{int(x_pos)}+{int(y)}'); self.msg_label.pack(expand=True); self.anim_static(t_ms, m)
        elif m["type"] == "קופץ": self.anim_jump(target, w, h, t_ms, m)

    def next_msg(self, m):
        if m["loop"]: self.show_msg()
        else:
            if self.msg_popup and self.msg_popup.winfo_exists(): self.msg_popup.destroy()
            self.current_msg_idx += 1; self.show_msg()

    def update_msg_color(self, m):
        self.color_idx = (self.color_idx + 1) % len(m["colors"]); self.msg_label.config(fg=m["colors"][self.color_idx])

    def anim_scroll(self, w, t, m):
        if not self.is_playing_messages or not self.msg_popup.winfo_exists(): return
        self.msg_x -= 8; self.msg_label.place(x=self.msg_x, y=0)
        if self.msg_x % 160 == 0: self.update_msg_color(m)
        if self.msg_x < -self.msg_label.winfo_reqwidth():
            if not m["loop"] and t <= 0: self.next_msg(m); return
            self.msg_x = w
        self.msg_job = self.root.after(20, lambda: self.anim_scroll(w, t - 20, m))

    def anim_static(self, t, m):
        if not self.is_playing_messages or not self.msg_popup.winfo_exists(): return
        self.update_msg_color(m)
        if not m["loop"] and t <= 0: self.next_msg(m)
        else: self.msg_job = self.root.after(500, lambda: self.anim_static(t - 500, m))

    def anim_jump(self, trg, w, h, t, m):
        if not self.is_playing_messages or not self.msg_popup.winfo_exists(): return
        self.msg_popup.geometry(f'{w}x{h}+{int(trg.x + random.randint(0, max(1, trg.width - w)))}+{int(trg.y + random.randint(0, max(1, trg.height - h)))}')
        self.update_msg_color(m)
        if not m["loop"] and t <= 0: self.next_msg(m)
        else: self.msg_job = self.root.after(1000, lambda: self.anim_jump(trg, w, h, t - 1000, m))

    def load_students_from_file(self):
        try:
            if HAS_OPENPYXL and os.path.exists("students.xlsx"): return [str(c.value).strip() for c in openpyxl.load_workbook("students.xlsx", data_only=True).active['A'] if c.value]
            elif os.path.exists("students.txt"):
                with open("students.txt", "r", encoding="utf-8") as f: return [l.strip() for l in f if l.strip()]
        except: pass
        return []
        
    def start_roulette(self):
        fn = self.load_students_from_file(); self.roulette_names = fn if fn else [n.strip() for n in self.roulette_names_var.get().split(',') if n.strip()]
        if len(self.roulette_names) < 2: return
        if self.roulette_popup and self.roulette_popup.winfo_exists(): self.roulette_popup.destroy()
        self.roulette_popup = tk.Toplevel(self.root); self.roulette_popup.overrideredirect(True); self.roulette_popup.attributes("-topmost", True); self.roulette_popup.attributes("-transparentcolor", "black"); self.roulette_popup.config(bg="black")
        self.roulette_label = tk.Label(self.roulette_popup, text="🎲 מערבב...", font=("Arial", 70, "bold"), fg="#00FFFF", bg="black"); self.roulette_label.pack(pady=20, padx=20)
        self.roulette_popup.update_idletasks(); t = self.get_target_monitor(); w, h = self.roulette_popup.winfo_width(), self.roulette_popup.winfo_height(); self.roulette_popup.geometry(f'+{int(t.x + (t.width/2) - (w/2))}+{int(t.y + (t.height/2) - (h/2))}')
        self.play_sound("drumroll")
        self.roulette_ticks = 0; self.roulette_delay = 50; self.spin_roulette()
        
    def spin_roulette(self):
        if not self.roulette_popup or not self.roulette_popup.winfo_exists(): return
        self.roulette_label.config(text=f"{random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}  {random.choice(self.roulette_names)}  {random.choice(['⚀','⚁','⚂','⚃','⚄','⚅'])}")
        self.roulette_ticks += 1
        if self.roulette_ticks < 30: 
            self.roulette_delay += int(self.roulette_ticks / 2)
            self.roulette_job = self.root.after(self.roulette_delay, self.spin_roulette)
        else: 
            self.roulette_label.config(text=f"⭐ {random.choice(self.roulette_names)} ⭐", fg=self.r_col_var.get(), font=("Arial", 120, "bold"))
            self.play_sound("tada")
            self.play_sound("applause")
            self.root.after(6000, lambda: self.roulette_popup.destroy() if self.roulette_popup else None)

    # --- סקרים ---
    def build_polls_tab(self):
        ttk.Label(self.tab_polls, text=self.T("📊 סקרים אינטראקטיביים", "📊 Interactive Polls"), font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.tab_polls, text=self.T("* טיפ: בקש מהתלמידים להשתמש בחותמות (Annotate) של זום כדי להצביע!", "* Tip: Ask students to use Zoom 'Annotate' stamps to vote!"), fg="blue").pack()
        
        form = tk.Frame(self.tab_polls); form.pack(pady=10)
        tk.Label(form, text=self.T("השאלה:", "Question:")).grid(row=0, column=1, sticky="e")
        self.poll_q_var = tk.StringVar(); ttk.Entry(form, textvariable=self.poll_q_var, width=40, font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)
        
        tk.Label(form, text=self.T("תשובות אפשריות (השאר ריק כדי להתעלם):", "Options (leave blank to ignore):"), fg="gray").grid(row=1, column=0, columnspan=2, sticky="e", pady=2)
        
        self.poll_opts = []
        for i in range(6):
            tk.Label(form, text=f"{i+1}.").grid(row=i+2, column=1, sticky="e")
            v = tk.StringVar(); self.poll_opts.append(v)
            ttk.Entry(form, textvariable=v, width=40).grid(row=i+2, column=0, pady=2)

        acts = tk.Frame(self.tab_polls); acts.pack(pady=5)
        
        self.poll_movable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(acts, text=self.T("חלון חופשי זז (לא על כל המסך)", "Movable Window"), variable=self.poll_movable_var).pack(side=tk.RIGHT, padx=15)
        
        ttk.Button(acts, text="➕ הוסף שאלה", command=self.add_poll).pack(side=tk.RIGHT, padx=5)
        ttk.Button(acts, text="▶️ הקרן סקר", command=self.show_poll).pack(side=tk.RIGHT, padx=5)
        ttk.Button(acts, text="⏹️ סגור סקר", command=self.close_poll).pack(side=tk.RIGHT, padx=5)
        
        self.poll_lb = tk.Listbox(self.tab_polls, height=6, justify="right", font=("Arial", 10)); self.poll_lb.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        bf = tk.Frame(self.tab_polls); bf.pack(fill=tk.X, pady=5, padx=10)
        ttk.Button(bf, text="🗑️ נקה הכל", command=self.clear_polls).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bf, text="❌ מחק שאלה נבחרת", command=self.remove_selected_poll).pack(side=tk.RIGHT, padx=5)
        
        self.current_poll_idx = 0

    def add_poll(self):
        q = self.poll_q_var.get(); opts = [v.get() for v in self.poll_opts if v.get().strip()]
        if not q or not opts: return
        self.polls_list.append({"q": q, "opts": opts}); self.poll_lb.insert(tk.END, q)
        self.poll_q_var.set(""); [v.set("") for v in self.poll_opts]
        if self.poll_popup and self.poll_popup.winfo_exists(): self.render_poll_content()

    def remove_selected_poll(self):
        sel = self.poll_lb.curselection()
        if sel: 
            idx = sel[0]; self.poll_lb.delete(idx); self.polls_list.pop(idx)
            if self.poll_popup and self.poll_popup.winfo_exists(): self.render_poll_content()

    def clear_polls(self): self.polls_list.clear(); self.poll_lb.delete(0, tk.END)
    def close_poll(self):
        if self.poll_popup and self.poll_popup.winfo_exists(): self.poll_popup.destroy()

    def show_poll(self):
        if not self.polls_list:
            q = self.poll_q_var.get(); opts = [v.get() for v in self.poll_opts if v.get().strip()]
            if not q or not opts: return
            self.polls_list.append({"q": q, "opts": opts}); self.poll_lb.insert(tk.END, q)
            
        sel = self.poll_lb.curselection()
        self.current_poll_idx = sel[0] if sel else 0
        self.close_poll()
        
        self.poll_popup = tk.Toplevel(self.root)
        
        is_movable = self.poll_movable_var.get()
        t = self.get_target_monitor()
        
        if not is_movable:
            self.poll_popup.overrideredirect(True)
            self.poll_popup.geometry(f'{t.width}x{t.height}+{t.x}+{t.y}')
            tk.Button(self.poll_popup, text="✕", font=("Arial", 16), bg="#2C3E50", fg="white", bd=0, command=self.close_poll).place(x=t.width-40, y=10)
        else:
            self.poll_popup.title(self.T("סקר פעיל", "Active Poll"))
            self.poll_popup.geometry(f'800x600+{int(t.x + (t.width/2) - 400)}+{int(t.y + (t.height/2) - 300)}')
            self.poll_popup.protocol("WM_DELETE_WINDOW", self.close_poll)

        self.poll_popup.attributes("-topmost", True)
        self.poll_popup.bind("<Escape>", lambda e: self.close_poll())
        self.poll_popup.bind("<Right>", lambda e: self.poll_nav(1))
        self.poll_popup.bind("<Left>", lambda e: self.poll_nav(-1))
        
        self.poll_popup.config(bg="#2C3E50")
        
        nav_f = tk.Frame(self.poll_popup, bg="#2C3E50"); nav_f.pack(side=tk.BOTTOM, pady=20)
        tk.Button(nav_f, text="< השאלה הקודמת", font=("Arial", 20), bg="#34495E", fg="white", bd=0, command=lambda: self.poll_nav(-1)).pack(side=tk.LEFT, padx=20)
        tk.Button(nav_f, text="השאלה הבאה >", font=("Arial", 20), bg="#34495E", fg="white", bd=0, command=lambda: self.poll_nav(1)).pack(side=tk.RIGHT, padx=20)

        self.poll_content_frame = tk.Frame(self.poll_popup, bg="#2C3E50"); self.poll_content_frame.place(relx=0.5, rely=0.45, anchor="center")
        self.poll_popup.focus_force(); self.render_poll_content(); self.play_sound("tada")

    def poll_nav(self, direction):
        if not self.polls_list: return
        self.current_poll_idx = (self.current_poll_idx + direction) % len(self.polls_list)
        self.render_poll_content(); self.play_sound("spring")

    def render_poll_content(self):
        if not self.poll_popup or not self.poll_popup.winfo_exists() or not self.polls_list: return
        for w in self.poll_content_frame.winfo_children(): w.destroy()
        p_data = self.polls_list[self.current_poll_idx]; t = self.get_target_monitor()
        tk.Label(self.poll_content_frame, text=p_data["q"], font=("Arial", 60, "bold"), fg="#F1C40F", bg="#2C3E50", wraplength=t.width-100 if not self.poll_movable_var.get() else 700).pack(pady=40)
        colors = ["#3498DB", "#E74C3C", "#2ECC71", "#9B59B6", "#E67E22", "#1ABC9C"]
        for i, opt in enumerate(p_data["opts"]):
            of = tk.Frame(self.poll_content_frame, bg="#2C3E50"); of.pack(fill=tk.X, pady=10)
            tk.Label(of, text=f".{i+1}", font=("Arial", 40, "bold"), fg=colors[i%len(colors)], bg="#2C3E50").pack(side=tk.RIGHT, padx=20)
            tk.Label(of, text=opt, font=("Arial", 40), fg="white", bg="#2C3E50").pack(side=tk.RIGHT)

    # --- משחקים ---
    def build_games_tab(self):
        hm_frame = tk.LabelFrame(self.tab_games, text="🎮 Hangman / איש תלוי", font=("Arial", 11, "bold")); hm_frame.pack(fill=tk.X, padx=10, pady=5)
        sf = tk.Frame(hm_frame); sf.pack(pady=5); self.hm_secret_var = tk.StringVar(); ttk.Entry(sf, textvariable=self.hm_secret_var, font=("Arial", 14), justify="center", show="*").pack(side=tk.RIGHT, padx=5); ttk.Button(sf, text="🚀 התחל", command=self.start_hangman).pack(side=tk.RIGHT)
        kf = tk.Frame(hm_frame); kf.pack(pady=5)
        
        for i, l in enumerate("קראטופשדגכעיחלזסבהנמצת"): 
            ttk.Button(kf, text=l, width=2, command=lambda x=l: self.guess_hm(x)).grid(row=i//11, column=i%11, padx=1, pady=1)
            
        kfe = tk.Frame(hm_frame); kfe.pack(pady=5)
        for i, l in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"): ttk.Button(kfe, text=l, width=2, command=lambda x=l: self.guess_hm(x)).grid(row=i//9, column=i%9, padx=1, pady=1)
        ttk.Button(hm_frame, text="סגור משחק", command=self.close_hangman).pack(pady=5)

        sc_frame = tk.LabelFrame(self.tab_games, text="🧩 מילה מבולגנת (Word Scramble)", font=("Arial", 11, "bold")); sc_frame.pack(fill=tk.X, padx=10, pady=5)
        ss = tk.Frame(sc_frame); ss.pack(pady=5); self.scramble_word_var = tk.StringVar(); ttk.Entry(ss, textvariable=self.scramble_word_var, font=("Arial", 14), justify="center", show="*").pack(side=tk.RIGHT, padx=5); ttk.Button(ss, text="🚀 בַּלְגֵּן!", command=self.start_scramble).pack(side=tk.RIGHT, padx=5)
        sctrl = tk.Frame(sc_frame); sctrl.pack(pady=5); ttk.Button(sctrl, text="✨ חשוף", command=self.reveal_scramble).pack(side=tk.RIGHT, padx=5); ttk.Button(sctrl, text="סגור", command=self.close_scramble).pack(side=tk.RIGHT, padx=5)

        math_frame = tk.LabelFrame(self.tab_games, text="🧮 אתגר חשבון מתקדם", font=("Arial", 11, "bold")); math_frame.pack(fill=tk.X, padx=10, pady=5)
        mf_ctrl = tk.Frame(math_frame); mf_ctrl.pack(pady=5)
        
        tk.Label(mf_ctrl, text="נושא:").pack(side=tk.RIGHT, padx=5)
        self.math_topic_var = tk.StringVar(value="חיבור/חיסור")
        ttk.Combobox(mf_ctrl, textvariable=self.math_topic_var, values=["חיבור/חיסור", "כפל/חילוק", "חזקות", "משוואות", "חקירת פונקציות", "בחירה מרובה"], width=15, state="readonly").pack(side=tk.RIGHT, padx=5)
        
        tk.Label(mf_ctrl, text="רמת קושי:").pack(side=tk.RIGHT, padx=5)
        self.math_diff_var = tk.StringVar(value="קל")
        ttk.Combobox(mf_ctrl, textvariable=self.math_diff_var, values=["קל", "בינוני", "קשה"], width=8, state="readonly").pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(mf_ctrl, text="🚀 התחל אתגר", command=self.start_math).pack(side=tk.RIGHT, padx=5)
        ttk.Button(mf_ctrl, text="✨ חשוף פתרון", command=self.reveal_math).pack(side=tk.RIGHT, padx=5)
        ttk.Button(math_frame, text="סגור משחק", command=self.close_math).pack(pady=5)

    def start_hangman(self):
        w = self.hm_secret_var.get().strip().upper()
        if not w: return
        self.hangman_word = w
        self.hangman_guesses = set([" ", "-", "'"]) 
        self.hangman_mistakes = 0
        self.close_hangman()
        
        self.hangman_popup = tk.Toplevel(self.root); self.hangman_popup.overrideredirect(True); self.hangman_popup.attributes("-topmost", True); self.hangman_popup.config(bg="#2C3E50")
        t = self.get_target_monitor(); self.hangman_popup.geometry(f'800x600+{int(t.x + (t.width/2) - 400)}+{int(t.y + (t.height/2) - 300)}')
        tk.Label(self.hangman_popup, text="🤔 " + self.T("מי מנחש?", "Who can guess?"), font=("Arial", 35, "bold"), fg="#F1C40F", bg="#2C3E50").pack(pady=10)
        self.hm_word_label = tk.Label(self.hangman_popup, font=("Courier", 60, "bold"), fg="white", bg="#2C3E50"); self.hm_word_label.pack(pady=10)
        
        self.hm_guessed_label = tk.Label(self.hangman_popup, font=("Arial", 16), fg="#AAB7B8", bg="#2C3E50")
        self.hm_guessed_label.pack()
        
        self.hm_drawing_label = tk.Label(self.hangman_popup, font=("Courier", 25, "bold"), fg="#E74C3C", bg="#2C3E50", justify="left"); self.hm_drawing_label.pack(pady=5)
        self.hm_msg_label = tk.Label(self.hangman_popup, font=("Arial", 30, "bold"), bg="#2C3E50"); self.hm_msg_label.pack(pady=5)
        self.hangman_popup.bind("<Key>", lambda e: self.guess_hm(e.char.upper()) if e.char.isalpha() or '\u0590'<=e.char<='\u05FF' else None); self.hangman_popup.focus_force(); self.play_sound("tada"); self.update_hm_ui()

    def guess_hm(self, l):
        if not self.hangman_popup or not self.hangman_popup.winfo_exists() or self.hangman_mistakes >= 6 or all(c in self.hangman_guesses for c in self.hangman_word): return
        
        hebrew_finals = {'כ': 'ך', 'מ': 'ם', 'נ': 'ן', 'פ': 'ף', 'צ': 'ץ', 'ך': 'כ', 'ם': 'מ', 'ן': 'נ', 'ף': 'פ', 'ץ': 'צ'}
        
        guesses_to_add = {l}
        if l in hebrew_finals:
            guesses_to_add.add(hebrew_finals[l])
            
        if guesses_to_add.issubset(self.hangman_guesses): return
        
        self.hangman_guesses.update(guesses_to_add)
        
        if any(c in self.hangman_word for c in guesses_to_add): 
            self.play_sound("applause")
        else: 
            self.hangman_mistakes += 1
            self.play_sound("oy_oy_oy")
            
        self.update_hm_ui()

    def update_hm_ui(self):
        display_chars = [c if c in self.hangman_guesses else "_" for c in self.hangman_word]
        
        if any('\u0590' <= c <= '\u05FF' for c in self.hangman_word):
            display_chars.reverse()
            
        display_str = " ".join(display_chars)
        self.hm_word_label.config(text=display_str)
        
        guessed_display = {g for g in self.hangman_guesses if g not in ['ך', 'ם', 'ן', 'ף', 'ץ']}
        guessed_list = sorted(list(guessed_display - {" ", "-", "'"}))
        self.hm_guessed_label.config(text="ניחשתם כבר: " + ", ".join(guessed_list) if guessed_list else "ניחשתם כבר: טרם")
        
        stages = ["\n\n\n\n\n____", "\n |\n |\n |\n |\n_|_", " ____\n |/\n |\n |\n |\n_|_", " ____\n |/  |\n |\n |\n |\n_|_", " ____\n |/  |\n |   O\n |\n |\n_|_", " ____\n |/  |\n |   O\n |  /|\\\n |\n_|_", " ____\n |/  |\n |   O\n |  /|\\\n |  / \\\n_|_"]
        self.hm_drawing_label.config(text=stages[self.hangman_mistakes])
        
        if all(c in self.hangman_guesses for c in self.hangman_word): 
            self.hm_msg_label.config(text="🎉 ניצחתם!!! 🎉", fg="#00FF00"); self.play_sound("tada")
        elif self.hangman_mistakes >= 6: 
            loss_word = self.hangman_word[::-1] if any('\u0590' <= c <= '\u05FF' for c in self.hangman_word) else self.hangman_word
            self.hm_msg_label.config(text=f"הפסדתם! המילה: {loss_word}", fg="#FF0000"); self.play_sound("bomb")

    def close_hangman(self):
        if self.hangman_popup and self.hangman_popup.winfo_exists(): self.hangman_popup.destroy()

    def start_scramble(self):
        w = self.scramble_word_var.get().strip()
        if len(w.replace(" ", "")) < 2: return
        self.close_scramble()
        
        scrambled_words = []
        for word in w.split(" "):
            chars = list(word)
            if len(chars) > 1:
                while chars == list(word): random.shuffle(chars)
            scrambled_words.append("".join(chars))
            
        final_scramble = "   ".join(scrambled_words) 
        
        self.scramble_popup = tk.Toplevel(self.root); self.scramble_popup.overrideredirect(True); self.scramble_popup.attributes("-topmost", True); self.scramble_popup.config(bg="#8E44AD")
        t = self.get_target_monitor(); self.scramble_popup.geometry(f'900x400+{int(t.x + (t.width/2) - 450)}+{int(t.y + (t.height/2) - 200)}')
        tk.Label(self.scramble_popup, text=self.T("מה מסתתר כאן?", "What's hiding here?"), font=("Arial", 40, "bold"), fg="#F1C40F", bg="#8E44AD").pack(pady=30)
        self.sc_word_label = tk.Label(self.scramble_popup, text=final_scramble, font=("Arial", 60, "bold"), fg="white", bg="#8E44AD", wraplength=850); self.sc_word_label.pack(pady=20)
        self.play_sound("spring")

    def reveal_scramble(self):
        if self.scramble_popup and self.scramble_popup.winfo_exists():
            w = self.scramble_word_var.get().strip()
            revealed = "   ".join(w.split(" "))
            self.sc_word_label.config(text=revealed, fg="#00FF00"); self.play_sound("tada"); self.root.after(4000, self.close_scramble)
            
    def close_scramble(self):
        if self.scramble_popup and self.scramble_popup.winfo_exists(): self.scramble_popup.destroy()

    def start_math(self):
        self.close_math()
        topic = self.math_topic_var.get()
        diff = self.math_diff_var.get()
        ans = ""
        q_str = ""
        
        if topic == "חיבור/חיסור":
            if diff == "קל": a, b = random.randint(1, 20), random.randint(1, 20)
            elif diff == "בינוני": a, b = random.randint(10, 100), random.randint(10, 100)
            else: a, b = random.randint(100, 999), random.randint(100, 999)
            op = random.choice(["+", "-"])
            if op == "-" and a < b: a, b = b, a
            ans = eval(f"{a}{op}{b}")
            q_str = f"{a} {op} {b} = ?"
            
        elif topic == "כפל/חילוק":
            if diff == "קל": a, b = random.randint(2, 10), random.randint(2, 10)
            elif diff == "בינוני": a, b = random.randint(2, 20), random.randint(2, 15)
            else: a, b = random.randint(10, 99), random.randint(2, 9)
            if random.choice(["*", "/"]) == "/":
                ans = a
                q_str = f"{a*b} / {b} = ?"
            else:
                ans = a * b
                q_str = f"{a} * {b} = ?"
                
        elif topic == "חזקות":
            if diff == "קל": a, b = random.randint(2, 5), 2
            elif diff == "בינוני": a, b = random.randint(2, 10), random.randint(2, 3)
            else: a, b = random.randint(2, 15), random.randint(2, 4)
            ans = a ** b
            q_str = f"{a}^{b} = ?"
            
        elif topic == "משוואות":
            x = random.randint(1, 15)
            if diff == "קל":
                b = random.randint(1, 20)
                ans = x
                q_str = f"x + {b} = {x+b}\nx = ?"
            elif diff == "בינוני":
                a = random.randint(2, 6); b = random.randint(1, 20)
                ans = x
                q_str = f"{a}x + {b} = {a*x+b}\nx = ?"
            else:
                a = random.randint(2, 5); b = random.randint(1, 20); c = random.randint(1, 5)
                d = (a*x + b) - (c*x)
                if d < 0: c, a = a, c; d = (a*x + b) - (c*x)
                ans = x
                q_str = f"{a}x + {b} = {c}x + {d}\nx = ?"

        elif topic == "חקירת פונקציות":
            if diff == "קל":
                b = random.randint(1, 20)
                ans = b
                q_str = f"מהי נקודת החיתוך עם ציר ה-Y?\ny = 3x + {b}"
            elif diff == "בינוני":
                a = random.choice([1, -1]); b = random.randint(-6, 6) * 2
                ans = int(-b / (2*a))
                q_str = f"מהו ה-X של קודקוד הפרבולה?\ny = {a}x^2 + {b}x + 5"
            else:
                a = random.randint(2, 5); n = random.randint(3, 5)
                ans = f"y' = {a*n}x^{n-1}"
                q_str = f"מהי הנגזרת?\ny = {a}x^{n}"
                
        elif topic == "בחירה מרובה":
            a, b = random.randint(10, 50), random.randint(10, 50)
            real_ans = a + b
            options = [real_ans, real_ans + 10, real_ans - random.randint(1,5), real_ans + random.randint(1,5)]
            random.shuffle(options)
            q_str = f"{a} + {b} = ?\n\nא) {options[0]}   ב) {options[1]}\nג) {options[2]}   ד) {options[3]}"
            ans = real_ans

        self.math_answer = str(ans)
        self.math_q_str = q_str
        
        self.math_popup = tk.Toplevel(self.root)
        self.math_popup.overrideredirect(True)
        self.math_popup.attributes("-topmost", True)
        self.math_popup.config(bg="#16A085")
        t = self.get_target_monitor()
        self.math_popup.geometry(f'800x400+{int(t.x + (t.width/2) - 400)}+{int(t.y + (t.height/2) - 200)}')
        
        tk.Label(self.math_popup, text="מי פותר ראשון? 🤔", font=("Arial", 40, "bold"), fg="#F1C40F", bg="#16A085").pack(pady=20)
        self.math_lbl = tk.Label(self.math_popup, text=self.math_q_str, font=("Arial", 50, "bold"), fg="white", bg="#16A085", justify="center")
        self.math_lbl.pack(pady=10)
        self.play_sound("spring")
        
    def reveal_math(self):
        if hasattr(self, 'math_popup') and self.math_popup.winfo_exists():
            topic = self.math_topic_var.get()
            if topic == "בחירה מרובה" or "\n" in self.math_q_str:
                self.math_lbl.config(text=f"{self.math_q_str}\n\nתשובה: {self.math_answer}", fg="#00FF00")
            else:
                self.math_lbl.config(text=f"{self.math_q_str[:-1]} {self.math_answer}", fg="#00FF00")
            self.play_sound("tada")
            self.root.after(5000, self.close_math)
            
    def close_math(self):
        if hasattr(self, 'math_popup') and self.math_popup.winfo_exists():
            self.math_popup.destroy()

    # --- פרומפטים ---
    def build_prompts_tab(self):
        f_top = tk.Frame(self.tab_prompts); f_top.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(f_top, text="סוג הפרומפט:").grid(row=0, column=1, sticky="e", pady=5)
        self.prompt_type_var = tk.StringVar(value=list(PROMPT_TEMPLATES.keys())[0])
        type_cb = ttk.Combobox(f_top, textvariable=self.prompt_type_var, values=list(PROMPT_TEMPLATES.keys()), width=40, state="readonly")
        type_cb.grid(row=0, column=0, sticky="e", pady=5)
        type_cb.bind("<<ComboboxSelected>>", self.update_prompt_warning)
        
        tk.Label(f_top, text="נושא (חובה):").grid(row=1, column=1, sticky="e", pady=5)
        self.prompt_subject_var = tk.StringVar()
        ttk.Entry(f_top, textvariable=self.prompt_subject_var, width=42).grid(row=1, column=0, sticky="e", pady=5)
        
        tk.Label(f_top, text="לדוגמה: פרוטוקול OSPF, פייתון או פרשת השבוע", fg="gray", font=("Arial", 8)).grid(row=2, column=0, sticky="e")
        
        tk.Label(f_top, text="סגנון עיצוב/כתיבה (לא חובה):").grid(row=3, column=1, sticky="e", pady=5)
        self.prompt_style_var = tk.StringVar(value="מקצועי וברור")
        ttk.Entry(f_top, textvariable=self.prompt_style_var, width=42).grid(row=3, column=0, sticky="e", pady=5)
        
        tk.Label(f_top, text="פירוט מדויק / תתי נושאים (לא חובה):").grid(row=4, column=1, sticky="e", pady=5)
        self.prompt_details_var = tk.StringVar()
        ttk.Entry(f_top, textvariable=self.prompt_details_var, width=42).grid(row=4, column=0, sticky="e", pady=5)

        self.prompt_warning_lbl = tk.Label(self.tab_prompts, text="", fg="red", font=("Arial", 10, "bold"))
        self.prompt_warning_lbl.pack(pady=2)

        tk.Button(self.tab_prompts, text="✨ נסח פרומפט", font=("Arial", 11, "bold"), bg="#3498DB", fg="white", command=self.generate_prompt).pack(pady=10, ipadx=10, ipady=3)

        warning_text = (
            "💡 הערה חשובה:\n"
            "לאחר העתקת הפרומפט והדבקתו ב-AI, מומלץ מאוד\n"
            "להוסיף מקורות מידע מדויקים או טקסטים קיימים שלך\n"
            "כדי לקבל תוצאה מותאמת אישית."
        )
        tk.Label(self.tab_prompts, text="\u202B" + warning_text + "\u202C", fg="blue", font=("Arial", 11, "bold"), justify="right").pack(pady=5, anchor="e", padx=20)

        self.prompt_output = tk.Text(self.tab_prompts, height=10, width=80, font=("Arial", 11), bg="#f9f9f9", relief="solid", bd=1)
        self.prompt_output.pack(padx=10, pady=5)
        
        tk.Button(self.tab_prompts, text="📋 העתק פרומפט", font=("Arial", 10), command=self.copy_prompt).pack(pady=5)

    def update_prompt_warning(self, event=None):
        ptype = self.prompt_type_var.get()
        if ptype in ["ויזואליזציה דינאמית", "חידון אינטראקטיבי", "בניית אתר מודרני", "יחידת לימוד שלמה"]:
            self.prompt_warning_lbl.config(text="* שים לב: עבור פרומפט זה יש לוודא שמצב Canvas / Artifacts מופעל ב-AI.")
        else:
            self.prompt_warning_lbl.config(text="")

    def generate_prompt(self):
        ptype = self.prompt_type_var.get()
        subject = self.prompt_subject_var.get().strip() or "[הכנס נושא כאן]"
        style = self.prompt_style_var.get().strip() or "סגנון חופשי"
        details = self.prompt_details_var.get().strip() or "אין בקשות מיוחדות."
        
        template = PROMPT_TEMPLATES.get(ptype, "")
        final_prompt = template.format(subject=subject, style=style, details=details)
        
        self.prompt_output.delete("1.0", tk.END)
        self.prompt_output.insert(tk.END, final_prompt)
        self.prompt_output.tag_configure("right", justify='right')
        self.prompt_output.tag_add("right", "1.0", "end")

    def show_quiet_notification(self, message, duration=1500):
        notif = tk.Toplevel(self.root)
        notif.overrideredirect(True)
        notif.attributes("-topmost", True)
        notif.config(bg="#2ECC71", bd=2, relief="solid")
        
        tk.Label(notif, text=message, font=("Arial", 12, "bold"), bg="#2ECC71", fg="white", padx=20, pady=10).pack()
        
        notif.update_idletasks()
        w, h = notif.winfo_width(), notif.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (w // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (h // 2)
        notif.geometry(f"+{x}+{y}")
        
        self.root.after(duration, notif.destroy)

    def copy_prompt(self):
        txt = self.prompt_output.get("1.0", tk.END).strip()
        if txt:
            self.root.clipboard_clear()
            self.root.clipboard_append(txt)
            self.show_quiet_notification("✅ הפרומפט הועתק בהצלחה!")

    # --- אודות ---
    def build_about_tab(self):
        main_frame = tk.Frame(self.tab_about, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(main_frame, text="ClassGadget - אולפן שידור מתקדם לזום", font=("Arial", 18, "bold"), fg="#2C3E50")
        title.pack(pady=(0, 15))

        desc_text = "תוכנה זו פותחה כדי לשדרג את חוויית הלמידה מרחוק ולהוסיף אינטראקטיביות, הנאה\nומעורבות לתלמידים דרך פופאפים, צלילים, משחקים, סקרים וכלים למורים.\nהמערכת מאפשרת שליטה חיה בזמן שיעור ללא צורך בהגדרות מורכבות."
        desc = tk.Label(main_frame, text=desc_text, font=("Arial", 12), justify="center", bg="#f9f9f9", relief="solid", bd=1, padx=15, pady=15)
        desc.pack(pady=5, fill=tk.X)

        creator_frame = tk.Frame(main_frame, bg="#e6f2ff", pady=15, padx=10, relief="ridge", bd=2)
        creator_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(creator_frame, text="פותח ע\"י: מיכאל תקשוב", font=("Arial", 14, "bold"), bg="#e6f2ff").pack()
        
        link_web = tk.Label(creator_frame, text="tikshuv-ccna.com", font=("Arial", 13, "underline"), fg="blue", cursor="hand2", bg="#e6f2ff")
        link_web.pack(pady=(5,0))
        link_web.bind("<Button-1>", lambda e: webbrowser.open_new("https://tikshuv-ccna.com"))

        inst_frame = tk.LabelFrame(main_frame, text="מדריך מקוצר", font=("Arial", 13, "bold"), padx=15, pady=15)
        inst_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        instructions = [
            ("שיתוף מסך:", "ודאו שאתם משתפים מסך מלא בזום ובחרו את המסך הרצוי בתפריט למעלה"),
            ("הקפצות:", "השתמשו בקיצורי המקלדת או בלחצנים כדי להקפיץ גיפים ואפקטים"),
            ("אינטראקציה:", "השתמשו ב-'משחקים' ו-'סקרים' להפעלה חיה של הכיתה"),
            ("התאמה אישית:", "העלו קבצי תמונה או שמע משלכם ישירות דרך המערכת"),
            ("פרומפטים:", "היעזרו במחולל הפרומפטים כדי לייצר חומרי לימוד איכותיים בבינה מלאכותית")
        ]
        
        for title_str, text_str in instructions:
            row_f = tk.Frame(inst_frame)
            row_f.pack(fill=tk.X, pady=4)
            tk.Label(row_f, text=text_str, font=("Arial", 12)).pack(side=tk.RIGHT)
            tk.Label(row_f, text=title_str, font=("Arial", 12, "bold"), fg="#2C3E50").pack(side=tk.RIGHT, padx=(0, 5))

        yt_frame = tk.Frame(main_frame, pady=20)
        yt_frame.pack()
        tk.Label(yt_frame, text="למדריך הוידאו המלא:", font=("Arial", 14, "bold")).pack(side=tk.RIGHT, padx=5)
        
        link_yt = tk.Label(yt_frame, text="▶️ צפו ביוטיוב", font=("Arial", 14, "underline"), fg="red", cursor="hand2")
        link_yt.pack(side=tk.RIGHT)
        link_yt.bind("<Button-1>", lambda e: webbrowser.open_new("https://www.youtube.com/")) 

    # --- מסכי המתנה ---
    def build_fullscreen_tab(self):
        ttk.Label(self.tab_fullscreen, text=self.T("מסכי המתנה מובנים", "Built-in Screensavers"), font=("Arial", 12, "bold")).pack(pady=5)
        
        time_frame = tk.Frame(self.tab_fullscreen); time_frame.pack(pady=5)
        self.fs_use_timer_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(time_frame, text=self.T("ספירה לאחור (דקות):", "Timer (min):"), variable=self.fs_use_timer_var).pack(side=tk.RIGHT, padx=5)
        self.fs_minutes_var = tk.StringVar(value="10")
        ttk.Entry(time_frame, textvariable=self.fs_minutes_var, font=("Arial", 12), width=4, justify="center").pack(side=tk.RIGHT)
        
        tk.Label(time_frame, text="מוזיקת רקע:").pack(side=tk.RIGHT, padx=(15, 5))
        self.fs_bgm_var = tk.StringVar(value="ללא")
        ttk.Combobox(time_frame, textvariable=self.fs_bgm_var, values=["ללא"] + list(BGM_CONFIG.keys()), state="readonly", width=12).pack(side=tk.RIGHT, padx=5)
        
        btns_frame = tk.Frame(self.tab_fullscreen); btns_frame.pack(pady=5)
        tk.Button(btns_frame, text="▶️ " + self.T("תיכף מתחילים", "Starting Soon"), font=("Arial", 11, "bold"), bg="#1A252C", fg="white", command=lambda: self.show_fullscreen("start")).pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)
        tk.Button(btns_frame, text="☕ " + self.T("הפסקת קפה", "Coffee Break"), font=("Arial", 11, "bold"), bg="#D35400", fg="white", command=lambda: self.show_fullscreen("break")).pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)
        
        ttk.Separator(self.tab_fullscreen, orient='horizontal').pack(fill=tk.X, pady=10)
        
        custom_frame = tk.LabelFrame(self.tab_fullscreen, text="🎨 מסך מותאם אישית", font=("Arial", 12, "bold")); custom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        f1 = tk.Frame(custom_frame); f1.pack(fill=tk.X, pady=5)
        tk.Label(f1, text="הטקסט שיוצג:").pack(side=tk.RIGHT, padx=5)
        self.fs_custom_text = tk.StringVar(value="הטקסט שלי"); ttk.Entry(f1, textvariable=self.fs_custom_text, font=("Arial", 12), width=35).pack(side=tk.RIGHT)
        
        f2 = tk.Frame(custom_frame); f2.pack(fill=tk.X, pady=5)
        tk.Label(f2, text="אימוג'י:").pack(side=tk.RIGHT, padx=5)
        self.fs_custom_emoji = tk.StringVar(value="")
        ttk.Entry(f2, textvariable=self.fs_custom_emoji, font=("Segoe UI Emoji", 12), width=10).pack(side=tk.RIGHT, padx=5)
        
        emo_frame = tk.Frame(f2)
        emo_frame.pack(side=tk.RIGHT, padx=5)
        for emo in ["🚀", "🌟", "🎉", "☕", "📚", "🏆", "⏳", "💡", "🎊", "🎈"]:
            tk.Button(emo_frame, text=emo, font=("Segoe UI Emoji", 10), command=lambda e=emo: self.fs_custom_emoji.set(self.fs_custom_emoji.get() + e)).pack(side=tk.RIGHT, padx=1)
        ttk.Button(emo_frame, text="נקה", width=4, command=lambda: self.fs_custom_emoji.set("")).pack(side=tk.RIGHT, padx=5)

        f3 = tk.Frame(custom_frame); f3.pack(fill=tk.X, pady=5)
        tk.Label(f3, text="צבע רקע:").pack(side=tk.RIGHT, padx=5)
        self.fs_bg_col = tk.StringVar(value="#2C3E50")
        btn_bg = tk.Button(f3, bg=self.fs_bg_col.get(), width=2, command=lambda: self.pick_color(self.fs_bg_col, btn_bg)); btn_bg.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(f3, text="צבע טקסט:").pack(side=tk.RIGHT, padx=5)
        self.fs_fg_col = tk.StringVar(value="#F1C40F")
        btn_fg = tk.Button(f3, bg=self.fs_fg_col.get(), width=2, command=lambda: self.pick_color(self.fs_fg_col, btn_fg)); btn_fg.pack(side=tk.RIGHT, padx=5)
        
        self.fs_rainbow_var = tk.BooleanVar(value=False); ttk.Checkbutton(f3, text="טקסט מחליף צבעים", variable=self.fs_rainbow_var).pack(side=tk.RIGHT, padx=15)
        
        f4 = tk.Frame(custom_frame); f4.pack(fill=tk.X, pady=5)
        tk.Label(f4, text="אנימציית טקסט:").pack(side=tk.RIGHT, padx=5)
        self.fs_anim_var = tk.StringVar(value="ללא")
        ttk.Combobox(f4, textvariable=self.fs_anim_var, values=["ללא", "קופץ", "רועד", "טיקר זז"], width=10, state="readonly").pack(side=tk.RIGHT, padx=5)
        
        tk.Label(f4, text="אפקט מסך:").pack(side=tk.RIGHT, padx=15)
        self.fs_effect_var = tk.StringVar(value="ללא")
        ttk.Combobox(f4, textvariable=self.fs_effect_var, values=["ללא", "קונפטי ובלונים"], width=15, state="readonly").pack(side=tk.RIGHT, padx=5)

        tk.Button(custom_frame, text="✨ הפעל מסך מותאם אישית", font=("Arial", 12, "bold"), bg="#8E44AD", fg="white", command=lambda: self.show_fullscreen("custom")).pack(pady=10, ipadx=10, ipady=5)

        ttk.Button(self.tab_fullscreen, text="⏹️ סגור מסך פעיל", style="Stop.TButton", command=self.close_fullscreen).pack(pady=10, ipadx=20, ipady=5)

    def show_fullscreen(self, screen_type):
        self.close_fullscreen()
        
        bgm_sel = self.fs_bgm_var.get()
        if bgm_sel != "ללא" and bgm_sel in BGM_CONFIG:
            self.play_bgm(BGM_CONFIG[bgm_sel])

        self.fs_popup = tk.Toplevel(self.root)
        self.fs_popup.overrideredirect(True)
        self.fs_popup.attributes("-topmost", True)
        self.fs_popup.bind("<Escape>", lambda e: self.close_fullscreen())
        target = self.get_target_monitor()
        self.fs_popup.geometry(f'{target.width}x{target.height}+{target.x}+{target.y}')
        
        if screen_type == "custom":
            bg = self.fs_bg_col.get()
            mt = self.fs_custom_text.get()
            tc = self.fs_fg_col.get()
            emo = self.fs_custom_emoji.get()
            self.fs_popup.config(bg=bg)
            
            self.fs_main_frame = tk.Frame(self.fs_popup, bg=bg)
            self.fs_main_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            self.fs_custom_lbl = tk.Label(self.fs_main_frame, text=mt, font=("Helvetica", 80, "bold"), fg=tc, bg=bg)
            self.fs_custom_lbl.pack(pady=10)
            
            if emo: tk.Label(self.fs_main_frame, text=emo, font=("Segoe UI Emoji", 60), bg=bg, fg=tc).pack(pady=10)
            
            if self.fs_use_timer_var.get():
                try: self.fs_time_left = int(self.fs_minutes_var.get()) * 60
                except: self.fs_time_left = 300
                self.fs_timer_label = tk.Label(self.fs_main_frame, text="", font=("Helvetica", 100, "bold"), fg="#FFFFFF", bg=bg); self.fs_timer_label.pack(pady=(20, 0)); self.update_fs_timer()
            
            self.fs_color_idx = 0
            self.fs_rainbow_colors = ["#FF5733", "#F1C40F", "#2ECC71", "#3498DB", "#9B59B6", "#FFC300", "#00FFFF"]
            self.run_custom_fs_animations(target)
            
        else:
            bg, mt, tc, emo = ("#1A252C", self.T("תיכף מתחילים...","Starting soon..."), "#F1C40F", "🚀 📚") if screen_type == "start" else ("#5C3A21", self.T("יצאנו להפסקת קפה","Coffee Break"), "#FFFFFF", "☕ 🥐")
            self.fs_popup.config(bg=bg); cf = tk.Frame(self.fs_popup, bg=bg); cf.place(relx=0.5, rely=0.5, anchor="center")
            tk.Label(cf, text=mt, font=("Helvetica", 70, "bold"), fg=tc, bg=bg).pack(pady=(0, 20))
            img_loaded = False
            for img_name in (["coffee.png", "coffee.gif"] if screen_type == "break" else ["start.png", "start.gif"]):
                path = os.path.join(GIF_FOLDER, img_name)
                if os.path.exists(path):
                    try:
                        if path.endswith(".gif"): AnimatedGif(cf, path, bg=bg).pack(pady=20)
                        else: img = Image.open(path); img.thumbnail((400, 400)); p = ImageTk.PhotoImage(img); l = tk.Label(cf, image=p, bg=bg); l.image = p; l.pack(pady=20)
                        img_loaded = True; break
                    except: pass
            if not img_loaded: tk.Label(cf, text=emo, font=("Segoe UI Emoji", 80), bg=bg, fg=tc).pack(pady=20)
            if self.fs_use_timer_var.get():
                try: self.fs_time_left = int(self.fs_minutes_var.get()) * 60
                except: self.fs_time_left = 300
                self.fs_timer_label = tk.Label(cf, text="", font=("Helvetica", 120, "bold"), fg="#FFFFFF", bg=bg); self.fs_timer_label.pack(pady=(40, 0)); self.update_fs_timer()

        tk.Button(self.fs_popup, text="✕", font=("Arial", 16), bg=bg, fg="white", bd=0, command=self.close_fullscreen).place(x=target.width - 40, y=10)

    def run_custom_fs_animations(self, target):
        if not self.fs_popup or not self.fs_popup.winfo_exists(): return
        
        if self.fs_rainbow_var.get() and hasattr(self, 'fs_custom_lbl'):
            self.fs_color_idx = (self.fs_color_idx + 1) % len(self.fs_rainbow_colors)
            self.fs_custom_lbl.config(fg=self.fs_rainbow_colors[self.fs_color_idx])
            
        anim_type = self.fs_anim_var.get()
        if anim_type != "ללא" and hasattr(self, 'fs_main_frame'):
            if anim_type == "רועד":
                dx = random.randint(-15, 15)
                dy = random.randint(-15, 15)
                self.fs_main_frame.place(relx=0.5, rely=0.5, x=dx, y=dy, anchor="center")
            elif anim_type == "קופץ":
                if not hasattr(self, 'fs_bounce_dx'): self.fs_bounce_dx, self.fs_bounce_dy, self.fs_bx, self.fs_by = 10, 10, target.width/2, target.height/2
                self.fs_bx += self.fs_bounce_dx
                self.fs_by += self.fs_bounce_dy
                if self.fs_bx > target.width - 200 or self.fs_bx < 200: self.fs_bounce_dx *= -1
                if self.fs_by > target.height - 100 or self.fs_by < 100: self.fs_bounce_dy *= -1
                self.fs_main_frame.place(x=self.fs_bx, y=self.fs_by, anchor="center")
            elif anim_type == "טיקר זז":
                if not hasattr(self, 'fs_ticker_x'): self.fs_ticker_x = target.width
                self.fs_ticker_x -= 5
                if self.fs_ticker_x < -500: self.fs_ticker_x = target.width
                self.fs_main_frame.place(x=self.fs_ticker_x, rely=0.5, anchor="w")

        if self.fs_effect_var.get() == "קונפטי ובלונים":
            if not hasattr(self, 'fs_particles'): self.fs_particles = []
            if random.random() < 0.2: 
                emo = random.choice(["🎈", "🎉", "✨", "🎊"])
                lbl = tk.Label(self.fs_popup, text=emo, font=("Segoe UI Emoji", random.randint(20,40)), bg=self.fs_bg_col.get())
                px = random.randint(0, target.width)
                lbl.place(x=px, y=-50)
                self.fs_particles.append({"lbl": lbl, "x": px, "y": -50, "dy": random.randint(3, 8)})
            
            active_particles = []
            for p in self.fs_particles:
                p["y"] += p["dy"]
                if p["y"] < target.height:
                    p["lbl"].place(x=p["x"], y=p["y"])
                    active_particles.append(p)
                else:
                    p["lbl"].destroy()
            self.fs_particles = active_particles

        job = self.fs_popup.after(50, lambda: self.run_custom_fs_animations(target))
        self.fs_anim_jobs.append(job)

    def update_fs_timer(self):
        if not self.fs_popup or not self.fs_popup.winfo_exists() or not hasattr(self, 'fs_timer_label'): return
        if self.fs_time_left > 0: mins, secs = divmod(self.fs_time_left, 60); self.fs_timer_label.config(text=f"{mins:02d}:{secs:02d}"); self.fs_time_left -= 1; self.fs_timer_job = self.fs_popup.after(1000, self.update_fs_timer)
        else: self.fs_timer_label.config(text="00:00", fg="#FF4500"); self.play_sound("alarm")

    def close_fullscreen(self):
        if self.fs_popup and self.fs_popup.winfo_exists():
            if self.fs_timer_job: self.root.after_cancel(self.fs_timer_job)
            for job in self.fs_anim_jobs: self.root.after_cancel(job)
            self.fs_anim_jobs.clear()
            if hasattr(self, 'fs_particles'):
                for p in self.fs_particles: p["lbl"].destroy()
                self.fs_particles.clear()
            
            if hasattr(self, 'fs_bounce_dx'): del self.fs_bounce_dx
            if hasattr(self, 'fs_ticker_x'): del self.fs_ticker_x
            
            self.fs_popup.destroy()
            pygame.mixer.music.stop()

    # --- אודיו מתקדם ---
    def find_audio_file(self, basename):
        for ext in ['.mp3', '.wav']:
            if os.path.exists(os.path.join(SOUND_FOLDER, basename + ext)): return os.path.join(SOUND_FOLDER, basename + ext)
        return None
    def play_sound(self, basename):
        fp = self.find_audio_file(basename)
        if fp: s = pygame.mixer.Sound(fp); s.set_volume(self.get_actual_sfx_volume()); s.play()
    def play_bgm(self, basename):
        fp = self.find_audio_file(basename)
        if fp: pygame.mixer.music.load(fp); pygame.mixer.music.set_volume(self.music_vol_var.get() * (0.0 if self.is_muted_var.get() else self.master_vol_var.get())); pygame.mixer.music.play(-1)
    def stop_all_audio(self): pygame.mixer.stop(); pygame.mixer.music.stop()
    def pause_audio(self): pygame.mixer.music.pause(); pygame.mixer.pause()
    def resume_audio(self): pygame.mixer.music.unpause(); pygame.mixer.unpause()

    # --- גיפים ---
    def trigger_random_gif(self, prefix, effect, play_sound_flag=True):
        if not os.path.exists(GIF_FOLDER): return
        vf = [f for f in os.listdir(GIF_FOLDER) if f.startswith(prefix) and f.lower().endswith(".gif")]
        if vf: self.trigger_gif(random.choice(vf), effect, play_sound_flag)
        
    def trigger_random_fireworks(self, prefix, play_sound_flag=True):
        if not os.path.exists(GIF_FOLDER): return
        vf = [f for f in os.listdir(GIF_FOLDER) if f.startswith(prefix) and f.lower().endswith(".gif")]
        if vf: self.trigger_fireworks(random.choice(vf), play_sound_flag)
        
    def get_target_monitor(self): return self.monitors[self.monitor_names.index(self.selected_monitor_var.get())]
    def create_base_popup(self):
        p = tk.Toplevel(self.root); p.overrideredirect(True); p.attributes("-topmost", True); p.attributes("-transparentcolor", "black"); p.config(bg="black"); return p
    
    def trigger_fireworks(self, specific_filename="firework.gif", play_sound_flag=True):
        for p in self.firework_popups:
            if p.winfo_exists(): p.destroy()
        self.firework_popups = []; t = self.get_target_monitor(); gif_path = os.path.join(GIF_FOLDER, specific_filename)
        if not os.path.exists(gif_path): return
        
        if play_sound_flag:
            self.play_sound("fireworks")
            
        for _ in range(10):
            p = self.create_base_popup(); self.firework_popups.append(p); AnimatedGif(p, gif_path, bg="black").pack(); p.update_idletasks(); w, h = p.winfo_width(), p.winfo_height()
            p.geometry('%dx%d+%d+%d' % (w, h, t.x + random.randint(0, t.width - w), t.y + random.randint(0, t.height - h)))
        self.root.after(FIREWORK_DISPLAY_TIME_MS, lambda: [p.destroy() for p in self.firework_popups if p.winfo_exists()])
    
    def trigger_gif(self, filename, effect, play_sound_flag=True):
        fp = os.path.join(GIF_FOLDER, filename)
        if not os.path.exists(fp): return
        
        if play_sound_flag:
            basename = os.path.splitext(filename)[0]
            self.play_sound(basename)

        if self.popup and self.popup.winfo_exists(): self.popup.destroy()
        self.popup = self.create_base_popup()
        
        gif_lbl = AnimatedGif(self.popup, fp, bg="black")
        gif_lbl.pack()
        
        txt = self.gif_text_var.get().strip()
        if txt:
            txt_lbl = tk.Label(self.popup, text=txt, font=("Arial", 30, "bold"), 
                               bg=self.gif_bg_var.get(), fg=self.gif_fg_var.get())
            txt_lbl.pack(side=tk.BOTTOM, fill=tk.X)

        self.popup.update_idletasks()
        w, h = self.popup.winfo_width(), self.popup.winfo_height(); t = self.get_target_monitor()
        
        if effect == "center": self.popup.geometry('%dx%d+%d+%d' % (w, h, int(t.x + (t.width / 2) - (w / 2)), int(t.y + (t.height / 2) - (h / 2)))); self.popup.after(DISPLAY_TIME_MS, self.popup.destroy)
        elif effect == "float_up": self.popup.geometry('%dx%d+%d+%d' % (w, h, int(t.x + (t.width / 2) - (w / 2)), int(t.y + t.height))); self.animate_window(t.x + (t.width / 2) - (w / 2), t.y + t.height, t.x + (t.width / 2) - (w / 2), t.y - h, w, h, 0, -5)
        elif effect == "slide_right": self.popup.geometry('%dx%d+%d+%d' % (w, h, int(t.x - w), int(t.y + (t.height / 2) - (h / 2)))); self.animate_window(t.x - w, t.y + (t.height / 2) - (h / 2), t.x + t.width, t.y + (t.height / 2) - (h / 2), w, h, 6, 0)
        elif effect == "drop_down": self.popup.geometry('%dx%d+%d+%d' % (w, h, int(t.x + (t.width / 2) - (w / 2)), int(t.y - h))); self.animate_window(t.x + (t.width / 2) - (w / 2), t.y - h, t.x + (t.width / 2) - (w / 2), t.y + t.height, w, h, 0, 4)
    
    def animate_window(self, cx, cy, tx, ty, w, h, sx, sy):
        if not self.popup or not self.popup.winfo_exists(): return
        if (sx > 0 and cx >= tx) or (sx < 0 and cx <= tx) or sx == 0:
            if (sy > 0 and cy >= ty) or (sy < 0 and cy <= ty) or sy == 0: self.popup.destroy(); return
        nx, ny = cx + sx, cy + sy; self.popup.geometry('%dx%d+%d+%d' % (w, h, int(nx), int(ny)))
        self.root.after(15, lambda: self.animate_window(nx, ny, tx, ty, w, h, sx, sy))

if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = ClassGadgetApp(root)
    root.mainloop()