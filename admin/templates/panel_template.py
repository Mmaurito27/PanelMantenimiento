import tkinter as tk
from logger import log, log_usuario
from theme import aplicar_tema
import session

def abrir_{panel_key}_panel():
    ventana = tk.Toplevel()
    ventana.title('{panel_name}')
    ventana.geometry('400x300')
    aplicar_tema(ventana, 'oscuro')
    tk.Label(ventana, text='{panel_name}', font=('Arial', 14)).pack(pady=10)
    tk.Button(ventana, text='Cerrar', command=ventana.destroy).pack(pady=20)
    log('Subpanel {panel_name} abierto')
    log_usuario(session.usuario_actual, 'Abrir subpanel {panel_name}')
