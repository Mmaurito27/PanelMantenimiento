import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import socket
import shutil
import os

from logger import log
from config import CONFIG


# ---------- FUNCIONES DE SISTEMA ----------
def n8n_disponible_en_path(): return shutil.which("n8n") is not None

def puerto_en_uso(puerto):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', puerto)) == 0

def abrir_n8n():
    try:
        if not n8n_disponible_en_path():
            resp = messagebox.askyesno("N8N no encontrado", "❗ N8N no está instalado.\n¿Deseás instalarlo ahora?")
            log("N8N no encontrado.", level="WARNING")
            if resp: instalar_dependencias_n8n()
            return

        if puerto_en_uso(5678):
            abrir = messagebox.askyesno("Ya se ejecuta", "El puerto 5678 ya está en uso.\n¿Abrir navegador igual?")
            if abrir: abrir_navegador_n8n()
            return

        subprocess.Popen("n8n", shell=True)
        abrir_navegador_n8n()
        log("N8N iniciado.")
    except Exception as e:
        messagebox.showerror("Error grave", f"N8N falló:\n{e}")
        log(f"Error al abrir N8N: {e}", level="ERROR")

def abrir_navegador_n8n():
    try:
        webbrowser.open("http://localhost:5678")
        log("Abrió navegador en N8N")
    except Exception as e:
        log(f"No se pudo abrir navegador: {e}", level="WARNING")

def instalar_dependencias_n8n():
    try:
        subprocess.run("npm install -g n8n", shell=True)
        log("Dependencias N8N instaladas")
    except Exception as e:
        log(f"Error al instalar N8N: {e}", level="ERROR")

def abrir_cv_analyzer():
    path = os.path.join("launchers", "cv_api_launcher.exe")
    try:
        if not os.path.exists(path):
            messagebox.showerror("Error", "cv_api_launcher.exe no está en /launchers/")
            log("cv_api_launcher.exe no encontrado", level="ERROR")
            return

        if puerto_en_uso(3001):
            seguir = messagebox.askyesno("Puerto ocupado", "El puerto 3001 ya está en uso.\n¿Ejecutar de todas formas?")
            if not seguir: return

        subprocess.Popen(path, shell=True)
        log("cv_api_launcher iniciado")
    except Exception as e:
        log(f"Error ejecutando CV Analyzer: {e}", level="ERROR")
        messagebox.showerror("Error grave", str(e))

# ---------- PANEL PRINCIPAL ----------
root = tk.Tk()
root.geometry("400x500")
root.resizable(False, False)
style = ttk.Style()
style.theme_use("clam")

# ---------- TEMA Y ESTILO ----------
modo_oscuro_activo = CONFIG.get("modo_oscuro", "false").lower() == "true"

class ThemeSwitch(ttk.Frame):
    def __init__(self, master, command=None, checked=False):
        super().__init__(master)
        self.command = command
        self.var = tk.BooleanVar(value=checked)
        self.canvas = tk.Canvas(self, width=50, height=24, highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.toggle)
        self.draw()

    def toggle(self, event=None):
        self.var.set(not self.var.get())
        self.draw()
        if self.command:
            self.command(self.var.get())

    def draw(self):
        self.canvas.delete("all")
        if self.var.get():
            self.canvas.create_rectangle(2,2,48,22, outline="#4caf50", fill="#4caf50", width=2)
            self.canvas.create_oval(28,4,46,20, fill="#ffffff", outline="#ffffff")
            self.canvas.create_text(14,12, text="☀️")
        else:
            self.canvas.create_rectangle(2,2,48,22, outline="#ccc", fill="#ccc", width=2)
            self.canvas.create_oval(4,4,22,20, fill="#ffffff", outline="#ffffff")
            self.canvas.create_text(36,12, text="🌙")

def aplicar_modo_oscuro(ventana, oscuro=True):
    if oscuro:
        ventana.configure(bg="#16202a")
        ventana.option_add("*TButton*background", "#1e1e1e")
        ventana.option_add("*TButton*foreground", "#ffffff")
        ventana.option_add("*Button*background", "#1e1e1e")
        ventana.option_add("*Button*foreground", "#ffffff")
        ventana.option_add("*Label*background", "#16202a")
        ventana.option_add("*Label*foreground", "#ffffff")
    else:
        ventana.configure(bg="#f0f0f0")
        ventana.option_add("*TButton*background", "#ffffff")
        ventana.option_add("*TButton*foreground", "#000000")
        ventana.option_add("*Button*background", "#ffffff")
        ventana.option_add("*Button*foreground", "#000000")
        ventana.option_add("*Label*background", "#f0f0f0")
        ventana.option_add("*Label*foreground", "#000000")

def toggle_modo_oscuro(valor: bool):
    global modo_oscuro_activo
    modo_oscuro_activo = valor
    aplicar_modo_oscuro(root, oscuro=modo_oscuro_activo)
    CONFIG['modo_oscuro'] = 'true' if modo_oscuro_activo else 'false'

theme_switch = ThemeSwitch(root, command=toggle_modo_oscuro, checked=modo_oscuro_activo)
theme_switch.place(x=340, y=10)

def abrir_documentacion():
    ruta = CONFIG.get("documentacion", os.path.join("docs", "manual.pdf"))
    if os.path.exists(ruta):
        webbrowser.open(ruta)
        log("Se abrió la documentación")
    else:
        messagebox.showwarning("No encontrado", "No se encontró la documentación")
        log(f"Documentación no encontrada: {ruta}", level="WARNING")

doc_btn = ttk.Button(root, text="📄", command=abrir_documentacion)
doc_btn.place(x=300, y=10)

aplicar_modo_oscuro(root, oscuro=modo_oscuro_activo)

# ---------- ÍCONO Y TÍTULO ----------
titulo = CONFIG.get("titulo", "Panel de Mantenimiento General")
root.title(titulo)
try:
    root.iconbitmap("assets/Guante.ico")
except Exception:
    pass

# ---------- CABECERA ----------
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

ttk.Label(main_frame, text=titulo, font=("Arial", 14, "bold")).pack(pady=(0,10))

# ---------- BOTONES DE ÁREA ----------
def abrir_rrhh():
    try:
        from subpanels import rrhh_panel
        rrhh_panel.abrir_rrhh_panel()
        log("Abrió subpanel RRHH")
    except Exception as e:
        log(f"Error abriendo RRHH: {e}", level="ERROR")
        messagebox.showerror("Error", str(e))

def modulo_en_desarrollo(nombre):
    log(f"Módulo en desarrollo: {nombre}")
    messagebox.showinfo("En desarrollo", f"🔧 El módulo de {nombre} aún no está disponible.")

areas = [
    ("RRHH", abrir_rrhh),
    ("Marketing", lambda: modulo_en_desarrollo("Marketing")),
    ("Comercial", lambda: modulo_en_desarrollo("Comercial")),
    ("Logística", lambda: modulo_en_desarrollo("Logística")),
    ("Sistemas", lambda: modulo_en_desarrollo("Sistemas")),
    ("Calidad", lambda: modulo_en_desarrollo("Calidad")),
    ("Dirección", lambda: modulo_en_desarrollo("Dirección")),
]

for nombre, accion in areas:
    ttk.Button(main_frame, text=nombre, width=30, command=accion).pack(fill="x", pady=3)

ttk.Button(main_frame, text="Salir", command=root.destroy).pack(pady=10)

# ---------- FINAL ----------
root.mainloop()
log("Panel general iniciado.")
