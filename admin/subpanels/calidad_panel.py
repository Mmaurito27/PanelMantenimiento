import customtkinter as ctk

def load_panel(parent):
    frame = ctk.CTkFrame(parent)
    ctk.CTkLabel(frame, text="Módulo Calidad en desarrollo").pack(padx=20, pady=20)
    return frame
