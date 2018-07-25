import json
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfile, asksaveasfile
from HoldemChartCreator.hands import hands
from HoldemChartCreator.draw import create_chart

DEFAULT_BG = "#e5e5e5"
DEFAULT_FG = "#000000"
DEFAULT_PICKER_COLOR = "#66ff66"
DEFAULT_OUTPUT_WIDTH = 512
DEFAULT_OUTPUT_HEIGHT = 512


class Cell(Button):
    def __init__(self, master=None, text='XX', **kw):
        super().__init__(master=master, text=text, width=3, relief=SUNKEN, state=DISABLED, bd=0, padx=2, pady=2, **kw)
        self.changed = False
        if 's' in text:
            self.combos = 4
        elif 'o' in text:
            self.combos = 12
        else:
            self.combos = 6

    def mouse_up(self):
        self.changed = False

    def mouse_over(self, mode, bg_color, fg_color):
        if not self.changed:
            if mode == 0:
                self.configure(bg=bg_color, state=NORMAL)
            elif mode == 1:
                self.configure(fg=fg_color, state=NORMAL)
            else:
                self.reset()
        self.changed = True

    def reset(self):
        self.configure(bg=DEFAULT_BG, fg=DEFAULT_FG, state=DISABLED)


class Chart(Frame):
    def __init__(self, master=None, toolbox=None, **kw):
        super().__init__(master=master, background='black', **kw)
        self.buttons = tuple(tuple(Cell(self, hand, bg=DEFAULT_BG, fg=DEFAULT_FG) for hand in row) for row in hands)
        self.mouse_pressed = False
        self.toolbox = toolbox
        self.bind_all("<Button-1>", self.mouse_down)
        self.bind_all("<ButtonRelease-1>", self.mouse_up)
        self.bind_all("<B1-Motion>", self.mouse_motion)

    def pack(self, **kw):
        super().pack(**kw)
        for i, row in enumerate(self.buttons):
            for j, button in enumerate(row):
                button.grid(row=i, column=j, padx=1, pady=1)

    def count_combos(self):
        return sum(button.combos * (1 if button['state'] == NORMAL else 0) for row in self.buttons for button in row)

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
                    button.mouse_over(self.toolbox.mode_selector.mode.get(), self.toolbox.cell_picker.button['bg'],
                                      self.toolbox.text_picker.button['bg'])
                    self.toolbox.combo_counter.update_counter()

    def reset(self):
        for row in self.buttons:
            for button in row:
                button.reset()
        self.toolbox.combo_counter.update_counter()

    def preview_chart(self):
        img = create_chart(int(self.toolbox.width.var.get()), int(self.toolbox.height.var.get()), self.to_dict())
        img.show()

    def save_chart(self):
        img = create_chart(int(self.toolbox.width.var.get()), int(self.toolbox.height.var.get()), self.to_dict())
        f = asksaveasfile(mode='wb', defaultextension='png')
        if f is None:
            return
        img.save(f)
        f.close()


    def to_dict(self):
        return [[{"fg": button['fg'], "bg": button['bg']} for button in row] for row in self.buttons]

    def load_colors(self, colors):
        for i, row in enumerate(colors):
            for j, color in enumerate(row):
                self.buttons[i][j].configure(bg=color['bg'], fg=color['fg'],
                                             state=DISABLED if color['bg'] == DEFAULT_BG else NORMAL)
        self.toolbox.combo_counter.update_counter()


class ComboCounter(Label):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.counter = StringVar(self)
        self['textvariable'] = self.counter
        self.chart = None

    def update_counter(self):
        combos = self.chart.count_combos()
        self.counter.set(f"Selected: {combos / 1326 * 100 :.2f}% ({combos} / 1326)")


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
        self.r2 = Radiobutton(self, text='Text', variable=self.mode, value=1)
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


class LabeledEntry(Frame):
    def __init__(self, master=None, text="Text", value=0, **kw):
        super().__init__(master=master, **kw)
        self.label = Label(self, text=text)
        self.var = StringVar(self)
        self.entry = Entry(self, textvariable=self.var)
        self.var.set(value)

    def pack(self, **kw):
        super().pack(**kw)
        self.label.pack(side=LEFT)
        self.entry.pack(side=LEFT)


class Toolbox(Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.combo_counter = ComboCounter(self)
        self.cell_picker = ColorPicker(self, "Cell Color:", DEFAULT_PICKER_COLOR)
        self.text_picker = ColorPicker(self, "Text Color:", DEFAULT_FG)
        self.mode_selector = ModeSelector(self)
        self.reset_button = Button(self, text="Reset chart")
        self.file_handler = FileHandler(self)
        self.width = LabeledEntry(self, "Width: ", DEFAULT_OUTPUT_WIDTH)
        self.height = LabeledEntry(self, "Height: ", DEFAULT_OUTPUT_HEIGHT)
        self.export_button = Button(self, text="Preview")
        self.save_button = Button(self, text="Export PNG")

    def bind_widgets(self, chart):
        self.combo_counter.chart = chart
        self.combo_counter.update_counter()
        self.reset_button.configure(command=chart.reset)
        self.export_button.configure(command=chart.preview_chart)
        self.save_button.configure(command=chart.save_chart)
        self.file_handler.chart = chart

    def pack(self, **kw):
        super().pack(**kw)
        self.combo_counter.pack(fill=X)
        self.cell_picker.pack(fill=X)
        self.text_picker.pack(fill=X)
        self.mode_selector.pack(fill=X)
        self.reset_button.pack(fill=X)
        self.file_handler.pack(fill=X)
        self.width.pack()
        self.height.pack()
        self.export_button.pack(fill=X)
        self.save_button.pack(fill=X)


def main():
    # WIDGETS
    root = Tk()
    tools = Toolbox(root)
    chart = Chart(root, tools)
    tools.bind_widgets(chart)
    # GEOMETRY
    chart.pack(side=LEFT)
    tools.pack(side=RIGHT)

    root.mainloop()


if __name__ == '__main__':
    main()
