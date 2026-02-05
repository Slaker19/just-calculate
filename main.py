import sys
import os
import gi
import math

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gdk, GLib, Adw

class CachyCalcWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("JustCalculate")
        self.set_default_size(360, 260) # Horizontal Layout
        self.set_resizable(False)

        # Use Adw.ToolbarView for layout structure
        toolbar_view = Adw.ToolbarView()
        self.set_content(toolbar_view)

        # HeaderBar for window controls (Min/Max/Close)
        header_bar = Adw.HeaderBar()
        header_bar.set_show_title(False) # Allow window to shrink by hiding title
        toolbar_view.add_top_bar(header_bar)

        # Load CSS
        self.load_css()

        # box container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5) # Reduced spacing
        vbox.set_margin_top(10) # Reduced margins
        vbox.set_margin_bottom(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        toolbar_view.set_content(vbox)

        # Display
        self.entry = Gtk.Entry()
        self.entry.add_css_class("calc-display") # Specific class
        self.entry.set_alignment(1.0) # Align right
        self.entry.set_editable(False)
        self.entry.set_placeholder_text("0")
        vbox.append(self.entry)

        # Grid for buttons
        grid = Gtk.Grid()
        grid.set_column_spacing(5) # Tighter for mini mode
        grid.set_row_spacing(5)
        grid.set_column_homogeneous(True) # Homogeneous keys
        grid.set_row_homogeneous(True)
        grid.set_halign(Gtk.Align.CENTER)
        vbox.append(grid)

        # Button layout - Scientific Compact Layout
        # Row 0: (, ), ^, √  <-- NEW
        # Row 1: C, DEL, %, /
        # Row 2: 7, 8, 9, *
        # Row 3: 4, 5, 6, -
        # Row 4: 1, 2, 3, +
        # Row 5: 0 (wide), ., =
        # CSS Classes: destructive-action, suggested-action, calc-func
        buttons = [
            ('(', 0, 0, 'calc-func'), (')', 1, 0, 'calc-func'), ('^', 2, 0, 'calc-func'), ('√', 3, 0, 'calc-func'),
            ('C', 0, 1, 'destructive-action'), ('DEL', 1, 1, 'destructive-action'), ('%', 2, 1, ''), ('/', 3, 1, ''),
            ('7', 0, 2, ''), ('8', 1, 2, ''), ('9', 2, 2, ''), ('*', 3, 2, ''),
            ('4', 0, 3, ''), ('5', 1, 3, ''), ('6', 2, 3, ''), ('-', 3, 3, ''),
            ('1', 0, 4, ''), ('2', 1, 4, ''), ('3', 2, 4, ''), ('+', 3, 4, ''),
            ('0', 0, 5, 'zero'), ('.', 2, 5, ''),          ('=', 3, 5, 'suggested-action') 
        ]

        for btn_data in buttons:
            label, col, row, css_class = btn_data
            button = Gtk.Button(label=label)
            button.add_css_class("calc-btn") # Add base class TO ALL buttons
            if css_class:
                button.add_css_class(css_class)
            
            # Standard Layout Logic
            if label == '0':
                # 0 spans 2 columns
                grid.attach(button, col, row, 2, 1)
                button.set_halign(Gtk.Align.FILL) # Zero fills its space
                button.set_hexpand(False)
            else:
                grid.attach(button, col, row, 1, 1)
                # CHANGE: Allow buttons to stretch horizontally
                button.set_halign(Gtk.Align.FILL) 
                button.set_valign(Gtk.Align.CENTER) 

            button.connect('clicked', self.on_button_clicked)

        # Key controller
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        try:
            css_path = os.path.join(os.path.dirname(__file__), 'style.css')
            css_provider.load_from_path(css_path)
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        except Exception as e:
            print(f"Failed to load CSS: {e}")

    def on_button_clicked(self, button):
        label = button.get_label()
        self.process_input(label)

    def on_key_pressed(self, controller, keyval, keycode, state):
        key = Gdk.keyval_name(keyval)
        
        # Mapping generic keys to calculator inputs
        mapping = {
            'Return': '=', 'KP_Enter': '=',
            'BackSpace': 'DEL',
            'Escape': 'C',
            'plus': '+', 'KP_Add': '+',
            'minus': '-', 'KP_Subtract': '-',
            'asterisk': '*', 'KP_Multiply': '*',
            'slash': '/', 'KP_Divide': '/',
            'period': '.', 'KP_Decimal': '.'
        }

        # Number keys
        if '0' <= key <= '9':
            self.process_input(key)
        elif key in mapping:
            self.process_input(mapping[key])
        
        # Also check for numbers on keypad (KP_0, etc)
        if key.startswith('KP_') and len(key) == 4 and '0' <= key[3] <= '9':
             self.process_input(key[3])

    def process_input(self, value):
        # Auto-clear if previous state was an error
        if self.entry.has_css_class("error-text"):
            self.entry.remove_css_class("error-text")
            self.entry.set_text("")
            
        current_text = self.entry.get_text()
        
        if value == 'C':
            self.entry.set_text("")
            self.entry.remove_css_class("error-text")
        elif value == 'DEL':
            self.entry.remove_css_class("error-text")
            self.entry.set_text(current_text[:-1])
        elif value == '√':
            try:
                if not current_text: return
                val = float(eval(current_text))
                if val < 0: raise ValueError
                res = math.sqrt(val)
                self.entry.set_text(str(res))
            except:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Math domain error: unreal number")
        elif value == '%':
            try:
                if not current_text: return
                val = float(eval(current_text))
                res = val / 100
                self.entry.set_text(str(res))
            except:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Error")
        elif value == '.':
            last_segment = current_text.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()[-1] if current_text else ""
            if '.' not in last_segment:
                self.entry.set_text(current_text + value)
        elif value == '=':
            try:
                expr = current_text.replace('^', '**')
                # Basic safety
                allowed = set("0123456789.+-*/%()^ ")
                
                result = eval(expr, {"__builtins__": None, "math": math, "sqrt": math.sqrt}, {})
                self.entry.set_text(str(result))
                self.entry.remove_css_class("error-text")
            except ZeroDivisionError:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Division by zero is impossible")
            except ValueError:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Math domain error: unreal number")
            except SyntaxError:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Invalid mathematical expression")
            except Exception:
                self.entry.add_css_class("error-text")
                self.entry.set_text("Invalid expression")
        else:
             self.entry.set_text(current_text + value)

class CachyCalcApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="slaker.alvinnas.JustCalculate")

    def do_startup(self):
        Gtk.Application.do_startup(self)
        # Force Dark Theme for modern look and title bar contrast
        settings = Gtk.Settings.get_default()
        if settings:
             settings.set_property("gtk-application-prefer-dark-theme", True)

    def do_activate(self):
        window = CachyCalcWindow(self)
        window.present()

if __name__ == '__main__':
    app = CachyCalcApp()
    app.run(sys.argv)
