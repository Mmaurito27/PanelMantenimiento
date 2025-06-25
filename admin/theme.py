THEMES = {
    "claro": {
        "bg": "#f0f0f0",
        "button_bg": "#ffffff",
        "button_fg": "#000000",
        "label_bg": "#f0f0f0",
        "label_fg": "#000000",
    },
    "oscuro": {
        "bg": "#16202a",
        "button_bg": "#1e1e1e",
        "button_fg": "#ffffff",
        "label_bg": "#16202a",
        "label_fg": "#ffffff",
    },
    "azul": {
        "bg": "#e8f1fa",
        "button_bg": "#0078d4",
        "button_fg": "#ffffff",
        "label_bg": "#e8f1fa",
        "label_fg": "#000000",
    },
    # Plantilla para nuevos temas (p.ej. "corporativo") puede agregarse
}


def aplicar_tema(ventana, nombre="claro"):
    """Aplica el tema indicado a la ventana."""
    tema = THEMES.get(nombre, THEMES["claro"])
    ventana.configure(bg=tema["bg"])
    ventana.option_add("*TButton*background", tema["button_bg"])
    ventana.option_add("*TButton*foreground", tema["button_fg"])
    ventana.option_add("*Button*background", tema["button_bg"])
    ventana.option_add("*Button*foreground", tema["button_fg"])
    ventana.option_add("*Label*background", tema["label_bg"])
    ventana.option_add("*Label*foreground", tema["label_fg"])

