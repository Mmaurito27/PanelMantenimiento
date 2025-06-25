import customtkinter as ctk
import os


def mostrar_login():
    ctk.set_appearance_mode("dark")
    win = ctk.CTk()
    win.title("Ingreso al Panel")
    win.geometry("300x220")
    win.resizable(False, False)

    ctk.CTkLabel(win, text="Área").pack(pady=(20, 0))
    area_var = ctk.StringVar(value="RRHH")
    area_menu = ctk.CTkOptionMenu(win, variable=area_var,
                                  values=["RRHH", "Marketing", "Calidad"])
    area_menu.pack(pady=5)

    ctk.CTkLabel(win, text="Usuario").pack(pady=(10, 0))
    user_entry = ctk.CTkEntry(win, width=200)
    user_entry.pack(pady=5)

    error_label = ctk.CTkLabel(win, text="", text_color="red")
    error_label.pack()

    def ingresar():
        usuario = user_entry.get().strip()
        area = area_var.get().strip()
        if not usuario or not area:
            error_label.configure(text="Completar todos los campos")
            return
        with open("session.py", "w", encoding="utf-8") as f:
            f.write(f"usuario_actual = {repr(usuario)}\n")
            f.write(f"area_actual = {repr(area)}\n")
        win.destroy()

    ctk.CTkButton(win, text="Ingresar", command=ingresar).pack(pady=15)
    win.mainloop()
