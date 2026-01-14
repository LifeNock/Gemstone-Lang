import tkinter as tk
import time

# --- GEMUI ENGINE ---
class GemUIEngine:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.elements = []
        self.width = 800
        self.height = 600
        self.title = "Gemstone Application"

    def init_window(self, title, w, h):
        self.root = tk.Tk()
        self.title = title
        self.width = w
        self.height = h
        self.root.title(self.title)
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)

    def create_surface(self):
        if not self.root: return
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def add_button(self, text, x, y, callback):
        if not self.root: return
        btn = tk.Button(self.root, text=text, command=callback, bg="#333", fg="white", font=("Consolas", 10))
        btn.place(x=x, y=y)

    def draw_rect(self, x, y, w, h, color):
        if not self.canvas: return
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="")

    def draw_text(self, text, x, y, size, color):
        if not self.canvas: return
        self.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", size), anchor="nw")

    def run(self):
        if self.root:
            self.root.mainloop()

# --- BRIDGE ---
gem_engine = GemUIEngine()

class BuiltinFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.arg_names = ['...args']

    def __repr__(self):
        return f"<native function {self.name}>"

def std_print(interpreter, args):
    print(*args)
    return None

def std_input(interpreter, args):
    if len(args) > 0: return input(args[0])
    return input()

def sys_start_app(interpreter, args):
    title = args[0] if len(args) > 0 else "Gem App"
    w = args[1] if len(args) > 1 else 600
    h = args[2] if len(args) > 2 else 400
    gem_engine.init_window(title, w, h)
    gem_engine.create_surface()
    return None

def sys_draw_box(interpreter, args):
    x, y, w, h = args[0], args[1], args[2], args[3]
    color = args[4] if len(args) > 4 else "white"
    gem_engine.draw_rect(x, y, w, h, color)
    return None

def sys_draw_text(interpreter, args):
    text = args[0]
    x, y = args[1], args[2]
    size = args[3] if len(args) > 3 else 12
    color = args[4] if len(args) > 4 else "white"
    gem_engine.draw_text(text, x, y, size, color)
    return None

def sys_ui_button(interpreter, args):
    text = args[0]
    x, y = args[1], args[2]
    func_node = args[3]

    def wrapper():
        interpreter.call_function(func_node, [])

    gem_engine.add_button(text, x, y, wrapper)
    return None

def sys_main_loop(interpreter, args):
    gem_engine.run()
    return None

# --- LOADER ---
def load_stdlib(symbol_table):
    symbol_table.set("print", BuiltinFunction("print", std_print))
    symbol_table.set("input", BuiltinFunction("input", std_input))
    
    symbol_table.set("GemApp", BuiltinFunction("GemApp", sys_start_app))
    symbol_table.set("DrawBox", BuiltinFunction("DrawBox", sys_draw_box))
    symbol_table.set("DrawText", BuiltinFunction("DrawText", sys_draw_text))
    symbol_table.set("UIButton", BuiltinFunction("UIButton", sys_ui_button))
    symbol_table.set("Run", BuiltinFunction("Run", sys_main_loop))
