from tkinter import *
from tkinter.colorchooser import askcolor
from PIL import ImageTk
from HoldemChartCreator.hands import hands


class Cell(Button):
    def __init__(self, master=None, text='XX', **kw):
        super().__init__(master=master, text=text, width=3, compound=LEFT, state=DISABLED)

    def mouse_up(self):
        self.changed = False

    def mouse_over(self, mode):
        pass


class Chart(Frame):
    def __init__(self, master=None, mode_selector=None, **kw):
        super().__init__(master=master, **kw)
        self.buttons = tuple(tuple(Cell(self, hand) for hand in row) for row in hands)
        self.mouse_pressed = False
        self.mode_selector = mode_selector
        self.bind("<Button-1>", self.mouse_down)
        self.bind("<ButtonRelease-1>", self.mouse_up)
        self.bind("<B1-Motion>", self.mouse_motion)

    def pack(self, **kw):
        super().pack(**kw)
        for i, row in enumerate(self.buttons):
            for j, button in enumerate(row):
                button.grid(row=i, column=j)

    def mouse_down(self, e):
        self.mouse_pressed = True
        self.update_containing_button(e)

    def mouse_up(self, e):
        self.mouse_pressed = False

    def mouse_motion(self, e):
        self.update_containing_button(e)

    def update_containing_button(self, e):
        for row in self.buttons:
            for button in row:
                if self.winfo_containing(e.x_root, e.y_root) is button:
                    button.mouse_over(self.mode_selector.mode)


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


def main():
    # WIDGETS
    root = Tk()
    tools = Frame(root)
    cell_picker = ColorPicker(tools, "Cell Color:", 'white')
    text_picker = ColorPicker(tools, "Text Color:", 'black')
    mode_selector = ModeSelector(tools)
    chart = Chart(root, mode_selector)
    # GEOMETRY
    chart.pack(side=LEFT)
    tools.pack(side=LEFT)
    cell_picker.pack(fill=X)
    text_picker.pack(fill=X)
    mode_selector.pack(fill=X)
    root.mainloop()


if __name__ == '__main__':
    main()
