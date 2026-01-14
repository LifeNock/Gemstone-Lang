import tkinter as tk
import os

# --- GEMUI ENGINE ---
class GemUIEngine:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.headless = False
        self.width = 800
        self.height = 600
        self.title = "Gemstone Application"

    def init_window(self, title, w, h):
        self.title = title
        self.width = w
        self.height = h
        try:
            self.root = tk.Tk()
            self.root.title(self.title)
            self.root.geometry(f"{self.width}x{self.height}")
            self.root.resizable(False, False)
        except Exception:
            self.headless = True
            print(f"!! NO DISPLAY DETECTED !!")
            print(f"!! Running in HEADLESS MODE (Text Only) !!")

    def create_surface(self):
        if self.headless: return
        if not self.root: return
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def add_button(self, text, x, y, callback):
        if self.headless: return
        if not self.root: return
        btn = tk.Button(self.root, text=text, command=callback, bg="#333", fg="white", font=("Consolas", 10))
        btn.place(x=x, y=y)

    def draw_rect(self, x, y, w, h, color, tag=""):
        if self.headless: return
        if not self.canvas: return
        # If a tag is provided, we can move this object later
        if tag:
            self.canvas.delete(tag) # Clear old pos
            self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="", tags=tag)
        else:
            self.canvas.create_rectangle(x, y, x+w, y+h, fill=color, outline="")

    def draw_text(self, text, x, y, size, color, tag=""):
        if self.headless: return
        if not self.canvas: return
        if tag: self.canvas.delete(tag)
        self.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", size), anchor="nw", tags=tag)

    def bind_key(self, key, callback):
        if self.headless: return
        if not self.root: return
        self.root.bind(key, lambda e: callback())

    def schedule(self, ms, callback):
        if self.headless: return
        if not self.root: return
        self.root.after(ms, callback)

    def run(self):
        if self.headless:
            print("!! Headless Simulation Running (Ctrl+C to stop) !!")
            try:
                while True: input()
            except: pass
        elif self.root:
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
    tag = args[5] if len(args) > 5 else "" 
    gem_engine.draw_rect(x, y, w, h, color, tag)
    return None

def sys_draw_text(interpreter, args):
    text = args[0]
    x, y = args[1], args[2]
    size = args[3] if len(args) > 3 else 12
    color = args[4] if len(args) > 4 else "white"
    tag = args[5] if len(args) > 5 else ""
    gem_engine.draw_text(text, x, y, size, color, tag)
    return None

def sys_ui_button(interpreter, args):
    text = args[0]
    x, y = args[1], args[2]
    func_node = args[3]
    def wrapper(): interpreter.call_function(func_node, [])
    gem_engine.add_button(text, x, y, wrapper)
    return None

def sys_on_key(interpreter, args):
    key = args[0]
    func_node = args[1]
    def wrapper(): interpreter.call_function(func_node, [])
    gem_engine.bind_key(key, wrapper)
    return None

def sys_loop(interpreter, args):
    ms = args[0]
    func_node = args[1]
    def wrapper(): interpreter.call_function(func_node, [])
    gem_engine.schedule(ms, wrapper)
    return None

def sys_main_loop(interpreter, args):
    gem_engine.run()
    return None

# --- LOADER ---
def load_stdlib(symbol_table):
    symbol_table.set("print", BuiltinFunction("print", std_print))
    symbol_table.set("input", BuiltinFunction("input", std_input))
    
    # GemUI Graphics
    symbol_table.set("GemApp", BuiltinFunction("GemApp", sys_start_app))
    symbol_table.set("DrawBox", BuiltinFunction("DrawBox", sys_draw_box))
    symbol_table.set("DrawText", BuiltinFunction("DrawText", sys_draw_text))
    
    # GemUI Interaction
    symbol_table.set("UIButton", BuiltinFunction("UIButton", sys_ui_button))
    symbol_table.set("OnKey", BuiltinFunction("OnKey", sys_on_key))
    symbol_table.set("After", BuiltinFunction("After", sys_loop))
    symbol_table.set("Run", BuiltinFunction("Run", sys_main_loop))
