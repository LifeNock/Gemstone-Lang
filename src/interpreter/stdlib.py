import tkinter as tk
import math
import random
import sys

class VirtualMachine:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.width = 600
        self.height = 400
        self.running = False
        self.headless = False
        
        self.keys_down = set()
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_down = False
        self.interpreter = None
        self.update_func = None
        self.images = {} 

    def init_hardware(self, w, h, title):
        self.width = w
        self.height = h
        try:
            self.root = tk.Tk()
            self.root.title(title)
            self.root.geometry(f"{self.width}x{self.height}")
            self.root.resizable(False, False)
            self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="black", highlightthickness=0)
            self.canvas.pack()
            self.root.bind("<KeyPress>", self._on_key_down)
            self.root.bind("<KeyRelease>", self._on_key_up)
            self.root.bind("<Motion>", self._on_mouse_move)
            self.root.bind("<Button-1>", self._on_mouse_click)
            self.root.bind("<ButtonRelease-1>", self._on_mouse_release)
            self.root.protocol("WM_DELETE_WINDOW", self._exit)
        except Exception as e:
            self.headless = True
            print(f"!! HEADLESS MODE ACTIVATED (Window failed: {e}) !!")
            print("Press Ctrl+C to exit.")

    def _on_key_down(self, e): self.keys_down.add(e.keysym.lower())
    def _on_key_up(self, e): self.keys_down.discard(e.keysym.lower())
    def _on_mouse_move(self, e): self.mouse_x, self.mouse_y = e.x, e.y
    def _on_mouse_click(self, e): self.mouse_down = True
    def _on_mouse_release(self, e): self.mouse_down = False
    def _exit(self): 
        self.running = False
        try: self.root.destroy()
        except: pass
        sys.exit(0)

    def load_image(self, path):
        if self.headless: return path
        try:
            img = tk.PhotoImage(file=path)
            self.images[path] = img
            return path
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None

    def draw_image(self, path, x, y):
        if self.headless or not self.canvas: return
        if path in self.images:
            self.canvas.create_image(x, y, image=self.images[path], anchor="nw")

    def clear_screen(self):
        if self.canvas: self.canvas.delete("all")

    def draw_rect(self, x, y, w, h, c):
        if self.canvas: self.canvas.create_rectangle(x, y, x+w, y+h, fill=c, outline="")

    def draw_text(self, text, x, y, s, c):
        if self.canvas: self.canvas.create_text(x, y, text=str(text), fill=c, font=("Consolas", s), anchor="nw")

    def start_loop(self, interpreter, func_node):
        self.interpreter = interpreter
        self.update_func = func_node
        self.running = True
        self._tick()
        if self.root: 
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self._exit()
        elif self.headless:
            try:
                while True: input()
            except: pass

    def _tick(self):
        if not self.running: return
        
        try:
            self.clear_screen()
            self.interpreter.call_function(self.update_func, [])
        except Exception as e:
            print(f"\nRUNTIME ERROR in GameLoop: {e}")
            self.running = False # Stop the loop so it doesn't spam errors
            return

        if self.root: self.root.after(16, self._tick)

vm = VirtualMachine()

def sys_init(interpreter, args):
    vm.init_hardware(args[0], args[1], args[2] if len(args)>2 else "Gemstone VM")
    return None

def sys_draw_rect(interpreter, args): vm.draw_rect(args[0], args[1], args[2], args[3], args[4]); return None
def sys_draw_text(interpreter, args): vm.draw_text(args[0], args[1], args[2], args[3], args[4]); return None
def sys_load_img(interpreter, args): return vm.load_image(args[0])
def sys_draw_img(interpreter, args): vm.draw_image(args[0], args[1], args[2]); return None

def sys_key_pressed(interpreter, args): 
    key = str(args[0]).lower()
    return 1 if key in vm.keys_down else 0

def sys_mouse_x(interpreter, args): return vm.mouse_x
def sys_mouse_y(interpreter, args): return vm.mouse_y
def sys_mouse_down(interpreter, args): return 1 if vm.mouse_down else 0
def sys_start(interpreter, args): vm.start_loop(interpreter, args[0]); return None

def std_print(interpreter, args): print(*args); return None
def std_len(interpreter, args): return len(args[0])
def std_push(interpreter, args): args[0].append(args[1]); return None
def std_pop(interpreter, args): return args[0].pop()

def math_random(interpreter, args): return random.randint(int(args[0]), int(args[1]))
def math_sin(interpreter, args): return math.sin(args[0])
def math_cos(interpreter, args): return math.cos(args[0])
def math_floor(interpreter, args): return math.floor(args[0])

def io_read(interpreter, args):
    try:
        with open(args[0], 'r') as f: return f.read()
    except: return ""

def io_write(interpreter, args):
    with open(args[0], 'w') as f: f.write(str(args[1]))
    return None

class BuiltinFunction:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.arg_names = ['...args']
    def __repr__(self): return f"<native {self.name}>"

def load_stdlib(symbol_table):
    symbol_table.set("print", BuiltinFunction("print", std_print))
    symbol_table.set("len", BuiltinFunction("len", std_len))
    symbol_table.set("push", BuiltinFunction("push", std_push))
    symbol_table.set("pop", BuiltinFunction("pop", std_pop))
    
    symbol_table.set("InitWindow", BuiltinFunction("InitWindow", sys_init))
    symbol_table.set("Rect", BuiltinFunction("Rect", sys_draw_rect))
    symbol_table.set("Text", BuiltinFunction("Text", sys_draw_text))
    symbol_table.set("LoadImage", BuiltinFunction("LoadImage", sys_load_img))
    symbol_table.set("DrawImage", BuiltinFunction("DrawImage", sys_draw_img))
    
    symbol_table.set("KeyDown", BuiltinFunction("KeyDown", sys_key_pressed))
    symbol_table.set("MouseX", BuiltinFunction("MouseX", sys_mouse_x))
    symbol_table.set("MouseY", BuiltinFunction("MouseY", sys_mouse_y))
    symbol_table.set("MouseDown", BuiltinFunction("MouseDown", sys_mouse_down))
    symbol_table.set("GameLoop", BuiltinFunction("GameLoop", sys_start))

    symbol_table.set("Random", BuiltinFunction("Random", math_random))
    symbol_table.set("Sin", BuiltinFunction("Sin", math_sin))
    symbol_table.set("Cos", BuiltinFunction("Cos", math_cos))
    symbol_table.set("Floor", BuiltinFunction("Floor", math_floor))

    symbol_table.set("ReadFile", BuiltinFunction("ReadFile", io_read))
    symbol_table.set("WriteFile", BuiltinFunction("WriteFile", io_write))
