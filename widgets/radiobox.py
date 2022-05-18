import tkinter as tk


class RadioBox(tk.Frame):
    """Панель из 2 кнопок RadioButton"""

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _make_widgets(self):
        self.inner_value = tk.BooleanVar()
        self.radio_yes = tk.Radiobutton(self, variable=self.inner_value, value=True, text='Да')
        self.radio_no = tk.Radiobutton(self, variable=self.inner_value, value=False, text='Нет')
        self.radio_yes.pack(side=tk.LEFT)
        self.radio_no.pack(side=tk.LEFT)

    def set(self, value):
        self.inner_value.set(bool(value))

    def get(self):
        return self.inner_value.get()


class PrinterOrientationRadioBox(tk.Frame):
    """Панель из 2 кнопок RadioButton для выбора ориентации печати принтера"""

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _make_widgets(self):
        tk.Label(self, text='Ориентация:').pack(side=tk.LEFT, padx=10)
        self.inner_value = tk.IntVar()
        self.radio_yes = tk.Radiobutton(self, variable=self.inner_value, value=1, text='Книжная')
        self.radio_no = tk.Radiobutton(self, variable=self.inner_value, value=2, text='Альбомная')
        self.radio_yes.pack(side=tk.LEFT)
        self.radio_no.pack(side=tk.LEFT)

    def set(self, value):
        self.inner_value.set(int(value))

    def get(self):
        return self.inner_value.get()


if __name__ == '__main__':
    root = tk.Tk()
    # rb = RadioBox(root)
    rb = PrinterOrientationRadioBox(root)
    rb.pack(padx=20, pady=20)

    rb.set(1)
    print(rb.get())

    def get_value():
        print(rb.get())

    btn = tk.Button(root, text='Get value', command=get_value)
    btn.pack()

    root.mainloop()