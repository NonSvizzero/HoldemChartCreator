import json
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.filedialog import askopenfile, asksaveasfile
from HoldemChartCreator.hands import hands
from HoldemChartCreator.draw import create_chart

DEFAULT_BG = "#C5BD96"
DEFAULT_FG = "#000000"
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

    def mouse_over(self, color):
        if not self.changed and self['background'] != color:
            self.configure(bg=color, state=NORMAL)
            self.changed = True
        else:
            self.reset()
            self.changed = False

    def reset(self):
        self.configure(bg=DEFAULT_BG, fg=DEFAULT_FG, state=DISABLED)


class Chart(Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, background='black', **kw)
        self.cells = tuple(tuple(Cell(self, hand, bg=DEFAULT_BG, fg=DEFAULT_FG) for hand in row) for row in hands)
        self.mouse_pressed = False
        self.bind_all("<Button-1>", self.mouse_down)
        self.bind_all("<ButtonRelease-1>", self.mouse_up)
        self.bind_all("<B1-Motion>", self.mouse_motion)
        self.toolbox = None
        self.last = None

    def pack(self, **kw):
        super().pack(**kw)
        for i, row in enumerate(self.cells):
            for j, button in enumerate(row):
                button.grid(row=i, column=j, padx=1, pady=1)

    def count_combos(self, color):
        return sum(cell.combos * (1 if cell['background'] == color else 0) for row in self.cells for cell in row)

    def update_color(self, old, new):
        for row in self.cells:
            for cell in row:
                if cell['background'] == old:
                    cell.configure(bg=new)

    def mouse_down(self, e):
        self.mouse_pressed = True
        self.update_containing_cell(e)

    def mouse_up(self, e):
        self.mouse_pressed = False
        for row in self.cells:
            for cell in row:
                cell.mouse_up()

    def mouse_motion(self, e):
        if self.mouse_pressed:
            self.update_containing_cell(e)

    def update_containing_cell(self, e):
        color = self.toolbox.range_container.box.active.button["background"]
        for row in self.cells:
            for cell in row:
                if self.winfo_containing(e.x_root, e.y_root) is cell and self.last is not cell:
                    cell.mouse_over(color)
                    self.toolbox.range_container.box.update_counters()
                    self.last = cell

    def reset(self):
        for row in self.cells:
            for cell in row:
                cell.reset()
        self.toolbox.range_container.box.update_counters()

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
        return [[{"fg": cell['fg'], "bg": cell['bg']} for cell in row] for row in self.cells]

    def load_colors(self, colors):
        for i, row in enumerate(colors):
            for j, color in enumerate(row):
                self.cells[i][j].configure(bg=color['bg'], fg=color['fg'],
                                           state=DISABLED if color['bg'] == DEFAULT_BG else NORMAL)
        self.toolbox.combo_counter.update_counters()


class ComboCounter(Label):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, width=20, **kw)
        self.counter = StringVar(self)
        self['textvariable'] = self.counter
        self.chart = None

    def update_counter(self, combos):
        self.counter.set(f"{combos / 1326 * 100 :.2f}% ({combos} / 1326)")


class Range(Frame):
    def __init__(self, master=None, text='Range', color='white', **kw):
        super().__init__(master=master, **kw)
        self.var = StringVar(self)
        self.entry = Entry(self, textvariable=self.var)
        self.entry.bind("<1>", self.set_active)
        self.var.set(text)
        self.button = Button(self, command=self.pick_color, bg=color, relief=SUNKEN, width=8)
        self.counter = ComboCounter(self)
        self.delete_button = Button(self, command=self.delete, text='-')

    def pick_color(self):
        (RGB, hex) = askcolor()
        self.button.configure(bg=hex)

    def count_combos(self, previous=0):
        combos = self.master.count_combos(self.button['background'])
        self.counter.update_counter(previous + combos)
        return previous + combos

    def set_active(self, e):
        self.master.active = self

    def pack(self, **kw):
        super().pack(**kw)
        self.entry.pack(side=LEFT)
        self.button.pack(side=LEFT, fill=X)
        self.counter.pack(side=LEFT)
        self.delete_button.pack(side=LEFT, fill=X)
        self.counter.update_counter(0)

    def delete(self):
        self.master.remove_range(self)

class RangeBox(Frame):
    COLORS = ["#D10ECF", "#D71042", "#DB7412", "#B3E014", "#1EE516", "#1992EF", "#411BF4"]

    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.chart = None
        self.ranges= []
        self.active = None

    def add_range(self):
        i = len(self.ranges)
        self.ranges.append(Range(master=self, text=f"Range #{i+1}", color=self.COLORS[i % len(self.COLORS)]))
        self.ranges[-1].pack()
        self.active = self.ranges[-1]

    def remove_range(self, range):
        if len(self.ranges) is 1:
            return
        range.destroy()
        self.ranges.remove(range)
        if self.active is range:
            self.active = self.ranges[0]

    def count_combos(self, color):
        return self.chart.count_combos(color)

    def update_counters(self, e=None):
        prev = 0
        for range in self.ranges:
            curr = range.count_combos(prev)
            if self.master.merge.get():
                prev = curr

    def update_color(self, old, new):
        self.chart.update_color(old, new)

    def pack(self, **kw):
        super().pack(**kw)
        self.add_range()

class RangeContainer(Frame):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
        self.box = RangeBox(self)
        self.add_button = Button(self, command=self.box.add_range, text='New Range')
        self.merge = IntVar()
        self.check_button = Checkbutton(self, text="Cumulate Ranges", var=self.merge)
        self.check_button.bind("<ButtonRelease-1>", self.box.update_counters)

    def pack(self, **kw):
        super().pack(**kw)
        self.box.pack()
        self.add_button.pack(fill=X)
        self.check_button.pack(fill=X)

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
        self.range_container = RangeContainer(self)
        self.reset_button = Button(self, text="Reset chart")
        self.file_handler = FileHandler(self)
        self.width = LabeledEntry(self, "Width: ", DEFAULT_OUTPUT_WIDTH)
        self.height = LabeledEntry(self, "Height: ", DEFAULT_OUTPUT_HEIGHT)
        self.export_button = Button(self, text="Preview")
        self.save_button = Button(self, text="Export PNG")

    def bind_widgets(self, chart):
        self.reset_button.configure(command=chart.reset)

    def pack(self, **kw):
        super().pack(**kw)
        self.range_container.pack(fill=X)
        self.reset_button.pack(fill=X)
        self.file_handler.pack(fill=X)
        self.width.pack()
        self.height.pack()
        self.export_button.pack(fill=X)
        self.save_button.pack(fill=X)

def bind_widgets(chart, toolbox):
    chart.toolbox = toolbox
    toolbox.reset_button.configure(command=chart.reset)
    toolbox.export_button.configure(command=chart.preview_chart)
    toolbox.save_button.configure(command=chart.save_chart)
    toolbox.file_handler.chart = chart
    toolbox.range_container.box.chart = chart
    toolbox.range_container.box.update_counters()

def main():
    # WIDGETS
    root = Tk()
    chart = Chart(root)
    tools = Toolbox(root)
    # GEOMETRY
    chart.pack(side=LEFT)
    tools.pack(side=RIGHT)
    # BINDING
    bind_widgets(chart, tools)

    root.mainloop()


if __name__ == '__main__':
    main()
