# CachyCalc

Una calculadora simple y moderna para Wayland/Hyprland escrita en Python y GTK4.

## Requisitos
- Python 3
- GTK4
- `python-gobject` (o equivalente en tu distro)

## Instalación

Simplemente clona el repositorio o descarga los archivos.

## Ejecución

```bash
cd /home/alvin/Apps/CachyCalc
python3 main.py
```

## Development / Desarrollo

If you encounter "Could not find import" errors in your editor (Si tienes errores de importación en tu editor):

1.  Install type stubs / Instala los stubs de tipo:
    ```bash
    pip install -r requirements.txt
    ```
2.  Restart your editor (VS Code is configured automatically via `.vscode/settings.json`).


## Características
- Diseño moderno compatible con temas oscuros.
- Operaciones básicas (+, -, *, /).
- Soporte para teclado (NumPad, Enter, Esc, Backspace).
