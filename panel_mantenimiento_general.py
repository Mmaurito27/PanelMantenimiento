import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import webbrowser
import socket
import shutil
import os
import sys
import importlib
import json
from datetime import datetime

from logger import log, log_usuario
from config import CONFIG
from theme import aplicar_tema
from update import detectar_modo_ejecucion
import update_checker


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
        log_usuario('Abrir N8N')
    except Exception as e:
        messagebox.showerror("Error grave", f"N8N falló:\n{e}")
        log(f"Error al abrir N8N: {e}", level="ERROR")
        log_usuario('Abrir N8N', resultado='ERROR')

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
        log_usuario('Ejecutar CV Analyzer')
    except Exception as e:
        log(f"Error ejecutando CV Analyzer: {e}", level="ERROR")
        messagebox.showerror("Error grave", str(e))
        log_usuario('Ejecutar CV Analyzer', resultado='ERROR')

def verificar_dependencias():
    """Comprueba la existencia de dependencias principales."""
    faltantes = []
    if shutil.which("python") is None:
        faltantes.append("Python")
    if shutil.which("node") is None:
        faltantes.append("Node")
    if shutil.which("n8n") is None:
        faltantes.append("N8N")
    if not os.path.exists(os.path.join("launchers", "cv_api_launcher.exe")):
        faltantes.append("cv_api_launcher.exe")

    if faltantes:
        messagebox.showwarning(
            "Dependencias faltantes",
            "No se encontraron: " + ", ".join(faltantes),
        )
        log("Faltan dependencias: " + ", ".join(faltantes), level="WARNING")
    else:
        log("Todas las dependencias están presentes.")


def _load_panels():
    """Carga la lista de paneles dinámicos desde config/panels.json"""
    path = os.path.join('config', 'panels.json')
    if not os.path.exists(path):
        return ['rrhh']
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return ['rrhh']


def _save_panels(paneles):
    path = os.path.join('config', 'panels.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(paneles, f, indent=2)


def backup_entorno():
    os.makedirs('backups', exist_ok=True)
    origen = os.path.join('config', 'entorno.txt')
    if os.path.exists(origen):
        ts = datetime.now().strftime('%Y-%m-%d_%H%M')
        dest = os.path.join('backups', f'entorno_backup_{ts}.txt')
        shutil.copy2(origen, dest)


def restaurar_backup():
    archivos = []
    if os.path.exists("backups"):
        archivos = [f for f in os.listdir("backups") if f.startswith("entorno_backup_")]
    if not archivos:
        messagebox.showinfo("Restaurar", "No hay backups disponibles")
        return
    win = tk.Toplevel(root)
    win.title("Restaurar backup")
    lb = tk.Listbox(win, width=50)
    for f in archivos:
        lb.insert("end", f)
    lb.pack(padx=10, pady=10)
    def restaurar():
        sel = lb.curselection()
        if not sel:
            return
        archivo = os.path.join("backups", lb.get(sel[0]))
        shutil.copy2(archivo, os.path.join("config", "entorno.txt"))
        messagebox.showinfo("Restaurar", "Archivo restaurado")
        win.destroy()
    ttk.Button(win, text="Restaurar", command=restaurar).pack(pady=5)

# ---------- PANEL PRINCIPAL ----------
root = tk.Tk()
root.geometry("400x500")
root.resizable(False, False)
style = ttk.Style()
style.theme_use("clam")

verificar_dependencias()
detectar_modo_ejecucion()
version_actual = update_checker.get_local_version()

# ---------- TEMA Y ESTILO ----------
modo_oscuro_activo = CONFIG.get("modo_oscuro", "false").lower() == "true"
tema_actual = "oscuro" if modo_oscuro_activo else "claro"

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

def toggle_modo_oscuro(valor: bool):
    global modo_oscuro_activo
    modo_oscuro_activo = valor
    backup_entorno()
    tema = "oscuro" if valor else "claro"
    aplicar_tema(root, tema)
    _update_sidebar_theme()
    CONFIG['modo_oscuro'] = 'true' if modo_oscuro_activo else 'false'

theme_switch = ThemeSwitch(root, command=toggle_modo_oscuro, checked=modo_oscuro_activo)
theme_switch.place(x=340, y=10)
Tooltip(theme_switch, 'Cambiar tema oscuro/claro')


class Tooltip:
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tip:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, background="yellow", relief="solid", borderwidth=1).pack()

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


def simple_input(prompt: str) -> str:
    win = tk.Toplevel(root)
    win.title('Input')
    tk.Label(win, text=prompt).pack()
    entry = tk.Entry(win, width=50)
    entry.pack()
    entry.focus()

    def submit():
        win.result = entry.get()
        win.destroy()

    tk.Button(win, text='Aceptar', command=submit).pack()
    win.grab_set()
    win.wait_window()
    return getattr(win, 'result', '')


def ver_log_extendido():
    win = tk.Toplevel(root)
    win.title('Log extendido')
    win.geometry('500x400')
    text = tk.Text(win, wrap='none')
    text.pack(fill='both', expand=True, side='left')
    sb = ttk.Scrollbar(win, command=text.yview)
    sb.pack(side='right', fill='y')
    text.configure(yscrollcommand=sb.set)
    try:
        with open(os.path.join('logs', 'panel.log'), 'r', encoding='utf-8') as f:
            for line in f:
                if '[ERROR]' in line:
                    tag = 'error'
                elif '[WARNING]' in line:
                    tag = 'warn'
                else:
                    tag = 'info'
                text.insert('end', line, tag)
    except Exception as e:
        text.insert('end', f'No se pudo cargar el log: {e}')

    text.tag_config('error', background='#ffcccc')
    text.tag_config('warn', background='#fff2cc')


def mostrar_modo_tecnico(event=None):
    clave = simple_input('🔒 Área restringida. Ingresá clave de sistemas:')
    if clave == '2391':
        frame_tecnico.pack(pady=(10, 5))
        slide_in(frame_tecnico)
        log('Modo técnico activado.')
    else:
        messagebox.showwarning('Acceso denegado', 'Clave incorrecta.')
        log('Intento fallido de acceso al modo técnico.')


def slide_in(frame, h=0, target=120):
    frame.pack_propagate(False)
    frame.configure(height=h)
    if h < target:
        frame.after(10, lambda: slide_in(frame, h+10, target))


def abrir_documentacion():
    ruta = CONFIG.get("documentacion", os.path.join("docs", "manual.pdf"))
    if os.path.exists(ruta):
        webbrowser.open(ruta)
        log("Se abrió la documentación local")
    else:
        url = CONFIG.get("documentacion_url", "https://example.com/manual")
        webbrowser.open(url)
        log(f"Documentación local no encontrada. Abrió {url}", level="WARNING")

doc_btn = ttk.Button(root, text="📘 Ayuda / Manual", command=abrir_documentacion)
doc_btn.place(x=220, y=10)
Tooltip(doc_btn, 'Abrir documentación del sistema')
ttk.Label(root, text=f"v{version_actual}").place(x=10, y=10)

aplicar_tema(root, tema_actual)

# ---------- BARRA LATERAL ----------
sidebar_visible = True
sidebar_frame = tk.Frame(root, width=40)
sidebar_frame.pack(side="left", fill="y")

def toggle_sidebar():
    global sidebar_visible
    if sidebar_visible:
        sidebar_frame.pack_forget()
        sidebar_visible = False
    else:
        sidebar_frame.pack(side="left", fill="y")
        sidebar_visible = True

toggle_btn = ttk.Button(root, text="≡", width=2, command=toggle_sidebar)
toggle_btn.place(x=60, y=10)

def _update_sidebar_theme():
    aplicar_tema(sidebar_frame, "oscuro" if modo_oscuro_activo else "claro")

_update_sidebar_theme()

ttk.Button(sidebar_frame, text="🏠", width=3, command=lambda: None).pack(pady=5)
ttk.Button(sidebar_frame, text="👤", width=3, command=lambda: abrir_rrhh()).pack(pady=5)
ttk.Button(sidebar_frame, text="📢", width=3, command=lambda: modulo_en_desarrollo('Marketing')).pack(pady=5)
ttk.Button(sidebar_frame, text="✅", width=3, command=lambda: modulo_en_desarrollo('Calidad')).pack(pady=5)

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
area_frame = ttk.Frame(main_frame)
area_frame.pack()
area_buttons = []


def abrir_subpanel(nombre):
    try:
        mod = importlib.import_module(f'subpanels.{nombre}_panel')
        getattr(mod, f'abrir_{nombre}_panel')()
        log(f'Abrió subpanel {nombre}')
        log_usuario(f'Abrir subpanel {nombre}')
    except Exception as e:
        log(f'Error abriendo {nombre}: {e}', level='ERROR')
        messagebox.showerror('Error', str(e))
        log_usuario(f'Abrir subpanel {nombre}', resultado='ERROR')


def actualizar_menu():
    for b in area_buttons:
        b.destroy()
    area_buttons.clear()
    for nombre in _load_panels():
        btn = ttk.Button(area_frame, text=nombre.capitalize(), width=30,
                         command=lambda n=nombre: abrir_subpanel(n))
        btn.pack(fill='x', pady=3)
        Tooltip(btn, f'Abrir módulo {nombre}')
        area_buttons.append(btn)


def crear_nuevo_panel():
    nombre = simple_input('Nombre del nuevo panel:')
    if not nombre:
        return
    key = nombre.lower().replace(' ', '_')
    tpl = os.path.join('templates', 'panel_template.py')
    if not os.path.exists(tpl):
        messagebox.showerror('Error', 'Plantilla no encontrada')
        return
    with open(tpl, 'r', encoding='utf-8') as f:
        contenido = f.read().replace('{panel_name}', nombre).replace('{panel_key}', key)
    destino = os.path.join('subpanels', f'{key}_panel.py')
    if os.path.exists(destino):
        messagebox.showerror('Error', 'El panel ya existe')
        return
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(contenido)
    paneles = _load_panels()
    if key not in paneles:
        paneles.append(key)
        _save_panels(paneles)
    actualizar_menu()
    messagebox.showinfo('Panel', 'Nuevo panel creado')
    log(f'Nuevo panel creado: {nombre}')
    log_usuario(f'Crear panel {nombre}')


actualizar_menu()

ttk.Button(main_frame, text="Salir", command=root.destroy).pack(pady=10)

# ---------- FRAME T\xc9CNICO ----------
frame_tecnico = ttk.LabelFrame(root, text="\ud83d\udd27 Modo T\xe9cnico", padding=10)
ttk.Button(frame_tecnico, text="Ver LOG extendido", command=ver_log_extendido).pack(pady=2)
ttk.Button(frame_tecnico, text="Crear nuevo panel", command=crear_nuevo_panel).pack(pady=2)
ttk.Button(frame_tecnico, text="Restaurar backup", command=restaurar_backup).pack(pady=2)
frame_tecnico.pack_forget()
root.bind("<Control-s>", mostrar_modo_tecnico)

# ---------- FINAL ----------
root.mainloop()
log("Panel general iniciado.")
