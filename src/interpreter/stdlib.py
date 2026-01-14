import tkinter as tk
import time

# --- VIRTUAL HARDWARE ---
class VirtualMachine:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.width = 600
        self.height = 400
        self.running = False
        
        # INPUT REGISTERS (Memory for inputs)
        self.keys_down = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = False
        
        # SYSTEM POINTERS
        self.interpreter = None
        self.update_func = None

    def init_hardware(self, w, h, title):
        self.width = w
        self.height = h
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black", highlightthickness=0)
        self.canvas.pack()

        # BIND RAW INPUTS (Mapping hardware events to memory)
        self.root.bind("<KeyPress>", self._on_key_down)
        self.root.bind("<KeyRelease>", self._on_key_up)
        self.root.bind("<Motion>", self._on_mouse_move)
        self.root.bind("<Button-1>", self._on_mouse_click)
        self.root.bind("<ButtonRelease-1>", self._on_mouse_release)
        
        # Kill switch
        self.root.protocol("WM_DELETE_WINDOW", self._exit)

    # --- INPUT DRIVERS ---
    def _on_key_down(self, e): self.keys_down.add(e.keysym.lower())
    def _on_key_up(self, e): self.keys_down.discard(e.keysym.lower())
    def _on_mouse_move(self, e): self.mouse_x, self.mouse_y = e.x, e.y
    def _on_mouse_click(self, e): self.mouse_down = True
    def _on_mouse_release(self, e): self.mouse_down = False
    def _exit(self): self.running = False; self.root.destroy()

    # --- GPU COMMANDS ---
    def clear_screen(self):
        self.canvas.delete("all")

    def draw_rect(self, x, y, w, h, c):
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=c, outline="")

    def draw_text(self, text, x, y, s, c):
        self.canvas.create_text(x, y, text=str(text), fill=c, font=("Consolas", s), anchor="nw")

    # --- THE CLOCK (60 FPS) ---
    def start_loop(self, interpreter, func_node):
        self.interpreter = interpreter
        self.update_func = func_node
        self.running = True
        self._tick()
        self.root.mainloop()

    def _tick(self):
        if not self.running: return
        
        # 1. Clear VRAM (Canvas)
        self.clear_screen()
        
        # 2. Execute Gemstone Code
        
        self.interpreter.call_function(self.update_func, [])
        
        # 3. Schedule next frame (approx 60 FPS = 16ms)
        self.root.after(16, self._tick)

# --- GLOBAL INSTANCE ---
vm = VirtualMachine()

# --- NATIVE FUNCTIONS MAPPED TO VM ---

def sys_init(interpreter, args):
    w, h = args[0], args[1]
    title = args[2] if len(args) > 2 else "Gemstone VM"
    vm.init_hardware(w, h, title)
    return None

def sys_draw_rect(interpreter, args):
    vm.draw_rect(args[0], args[1], args[2], args[3], args[4])
    return None

def sys_draw_text(interpreter, args):
    vm.draw_text(args[0], args[1], args[2], args[3], args[4])
    return None

# INPUT POLLING (Asking the hardware "Is this button pressed?")
def sys_key_pressed(interpreter, args):
    key = args[0].lower()
    return 1 if key in vm.keys_down else 0

def sys_mouse_x(interpreter, args): return vm.mouse_x
def sys_mouse_y(interpreter, args): return vm.mouse_y
def sys_mouse_down(interpreter, args): return 1 if vm.mouse_down else 0

# SYSTEM START
def sys_start(interpreter, args):
    func_node = args[0] # The user passes their 'main' loop function
    vm.start_loop(interpreter, func_node)
    return None

def std_print(interpreter, args):
    print(*args)
    return None

# --- LOADER ---
class BuiltinFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.arg_names = ['...args']
    def __repr__(self): return f"<native {self.name}>"

def load_stdlib(symbol_table):
    symbol_table.set("print", BuiltinFunction("print", std_print))
    
    # GPU
    symbol_table.set("InitWindow", BuiltinFunction("InitWindow", sys_init))
    symbol_table.set("Rect", BuiltinFunction("Rect", sys_draw_rect))
    symbol_table.set("Text", BuiltinFunction("Text", sys_draw_text))
    
    # INPUT
    symbol_table.set("KeyDown", BuiltinFunction("KeyDown", sys_key_pressed))
    symbol_table.set("MouseX", BuiltinFunction("MouseX", sys_mouse_x))
    symbol_table.set("MouseY", BuiltinFunction("MouseY", sys_mouse_y))
    symbol_table.set("MouseDown", BuiltinFunction("MouseDown", sys_mouse_down))
    
    # SYSTEM
    symbol_table.set("GameLoop", BuiltinFunction("GameLoop", sys_start))
