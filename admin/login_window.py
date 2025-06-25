import customtkinter as ctk
import os


def mostrar_login() -> bool:
    """Muestra la ventana de login y retorna True si se ingresaron datos."""

    ctk.set_appearance_mode("dark")
    win = ctk.CTk()
    win.title("Ingreso al Panel")
    win.geometry("300x220")
    win.resizable(False, False)

    if os.path.exists("assets/Guante.ico"):
        try:
            win.iconbitmap("assets/Guante.ico")
        except Exception:
            pass

    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
    y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")

    ctk.CTkLabel(win, text="Área").pack(pady=(20, 0))
    area_var = ctk.StringVar(value="RRHH")
    ctk.CTkOptionMenu(win, variable=area_var,
                      values=["RRHH", "Marketing", "Calidad"]).pack(pady=5)

    ctk.CTkLabel(win, text="Usuario").pack(pady=(10, 0))
    user_entry = ctk.CTkEntry(win, width=200)
    user_entry.pack(pady=5)
    user_entry.focus()

    error_label = ctk.CTkLabel(win, text="", text_color="red")
    error_label.pack()

    result = {"ok": False}

    def ingresar():
        usuario = user_entry.get().strip()
        area = area_var.get().strip()
        if not usuario:
            error_label.configure(text="Ingresá un usuario")
            return
        with open("session.py", "w", encoding="utf-8") as f:
            f.write(f"usuario_actual = {repr(usuario)}\n")
            f.write(f"area_actual = {repr(area)}\n")
        result["ok"] = True
        win.destroy()

    def on_close():
        result["ok"] = False
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkButton(win, text="Ingresar", command=ingresar).pack(pady=15)
    win.mainloop()
    return result["ok"]
