import tkinter.ttk as ttk


class ComboboxDict(ttk.Combobox):
    """Combobox для работы со словарем"""

    def __init__(self, master=None, **kw):
        self.inner_dict = None

        if 'values' in kw and isinstance(kw['values'], dict):
            kw['values'] = self._prepare_if_dict(kw['values'])

        super().__init__(master, **kw)

    def __setitem__(self, key, value):
        if key == 'values' and isinstance(value, dict):
            value = self._prepare_if_dict(value)
        super().__setitem__(key, value)

    def _prepare_if_dict(self, input_dict):
        """Если получен словарь для values, то подготавливаем его к работе"""
        self.inner_dict = input_dict
        return list(self.inner_dict.values())

    def get(self):
        """Переопределить метод get (унаследованный из tkinter.Entry)
        
        Нужно получить не содержимое Entry, а номер выбранной позиции
        и по ней отдать ключ словаря.
        """
        return list(self.inner_dict.keys())[self.current()]

    def get_keys(self):
        """Вернуть ключи словаря"""
        if self.inner_dict is not None:
            return list(self.inner_dict.keys())


if __name__ == '__main__':
    my_dict = {
        '1-dict': 'First',
        '2-dict': 'Second',
        '3-dict': 'Tale',
        '4-dict': 'End of dict',
    }
    def print_current(event):
        print(event.widget.get())

    import tkinter as tk
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack(expand=tk.YES, fill=tk.BOTH, padx=10, pady=10)

    tk.Label(frame, text='Тест ttk.Combobox, принимающего словарь').pack()

    combo = ComboboxDict(frame)#, values=my_dict)
    combo.pack()
    combo.state(['readonly'])
    combo.bind('<<ComboboxSelected>>', print_current)
    combo['values'] = my_dict

    root.mainloop()