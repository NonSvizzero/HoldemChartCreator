import json
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfile, asksaveasfile
from PIL import ImageTk
from HoldemChartCreator.hands import hands

DEFAULT_BG = "#e5e5e5"
DEFAULT_FG = "#000000"


class Cell(Button):
    def __init__(self, master=None, text='XX', **kw):
        super().__init__(master=master, text=text, width=3, relief=SUNKEN, bd=0, padx=2, pady=2, **kw)
        self.changed = False

    def mouse_up(self):
        self.changed = False

    def mouse_over(self, mode, bg_color, fg_color):
        if not self.changed:
            if mode == 0:
                self.configure(bg=bg_color)
            elif mode == 1:
                self.configure(fg=fg_color)
            else:
                self.reset()
        self.changed = True

    def reset(self):
        self.configure(bg=DEFAULT_BG, fg=DEFAULT_FG)


class Chart(Frame):
    #todo insert range percentage calculator
    def __init__(self, master=None, mode_selector=None, cell_picker=None, text_picker=None, **kw):
        super().__init__(master=master, background='black', **kw)
        self.buttons = tuple(tuple(Cell(self, hand, bg=DEFAULT_BG, fg=DEFAULT_FG) for hand in row) for row in hands)
        self.mouse_pressed = False
        self.mode_selector = mode_selector
        self.cell_picker = cell_picker
        self.text_picker = text_picker
        self.bind_all("<Button-1>", self.mouse_down)
        self.bind_all("<ButtonRelease-1>", self.mouse_up)
        self.bind_all("<B1-Motion>", self.mouse_motion)

    def pack(self, **kw):
        super().pack(**kw)
        for i, row in enumerate(self.buttons):
            for j, button in enumerate(row):
                button.grid(row=i, column=j, padx=1, pady=1)

    def mouse_down(self, e):
        self.mouse_pressed = True
        self.update_containing_button(e)

    def mouse_up(self, e):
        self.mouse_pressed = False
        for row in self.buttons:
            for button in row:
                button.mouse_up()

    def mouse_motion(self, e):
        if self.mouse_pressed:
            self.update_containing_button(e)

    def update_containing_button(self, e):
        for row in self.buttons:
            for button in row:
                if self.winfo_containing(e.x_root, e.y_root) is button:
                    button.mouse_over(self.mode_selector.mode.get(), self.cell_picker['bg'], self.text_picker['bg'])

    def reset(self):
        for row in self.buttons:
            for button in row:
                button.reset()

    def to_dict(self):
        return [[{"fg": button['fg'], "bg": button['bg']} for button in row] for row in self.buttons]

    def load_colors(self, colors):
        for i, row in enumerate(colors):
            for j, color in enumerate(row):
                self.buttons[i][j].configure(bg=color['bg'], fg=color['fg'])


class ColorPicker(Frame):
    def __init__(self, master=None, label='Label', color='white', **kw):
        super().__init__(master=master, **kw)
        self.label = Label(self, text=label, width=9)
        self.button = Button(self, command=self.pick_color, bg=color, relief=SUNKEN, width=8)

    def pick_color(self):
        (RGB, hex) = askcolor()
        self.button.configure(bg=hex)

    def pack(self, **kw):
        super().pack(**kw)
        self.label.pack(side=LEFT)
        self.button.pack(side=LEFT, fill=X)


class ModeSelector(Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.mode = IntVar()  # 0 = cell, 1 = flag, 2 = clear
        self.r1 = Radiobutton(self, text='Cell', variable=self.mode, value=0)
        self.r2 = Radiobutton(self, text='Flag', variable=self.mode, value=1)
        self.r3 = Radiobutton(self, text='Clear', variable=self.mode, value=2)

    def pack(self, **kw):
        super().pack(**kw)
        self.r1.pack(side=LEFT)
        self.r2.pack(side=LEFT)
        self.r3.pack(side=LEFT)


class FileHandler(Frame):
    def __init__(self, master=None, chart=None, **kw):
        super().__init__(master=master, **kw)
        self.chart = chart
        self.save_button = Button(self, text="Save", command=self.save)
        self.load_button = Button(self, text="Load", command=self.load)

    def save(self):
        f = asksaveasfile(defaultextension='.json')
        if f is None:
            return
        json.dump(self.chart.to_dict(), f)
        f.close()

    def load(self):
        f = askopenfile()
        if f is None:
            return
        colors = json.load(f)
        self.chart.load_colors(colors)
        f.close()

    def pack(self, **kw):
        super().pack(**kw)
        self.save_button.pack(side=LEFT, fill=X)
        self.load_button.pack(side=RIGHT, fill=X)

def main():
    # WIDGETS
    root = Tk()
    tools = Frame(root)
    cell_picker = ColorPicker(tools, "Cell Color:", DEFAULT_BG)
    text_picker = ColorPicker(tools, "Text Color:", DEFAULT_FG)
    mode_selector = ModeSelector(tools)
    chart = Chart(root, mode_selector, cell_picker.button, text_picker.button)
    reset_button = Button(tools, text="Reset chart", command=chart.reset)
    file_handler = FileHandler(tools, chart)
    # GEOMETRY
    chart.pack(side=LEFT)
    tools.pack(side=RIGHT)
    cell_picker.pack(fill=X)
    text_picker.pack(fill=X)
    mode_selector.pack(fill=X)
    reset_button.pack(fill=X)
    file_handler.pack(fill=X)
    root.mainloop()


if __name__ == '__main__':
    main()
