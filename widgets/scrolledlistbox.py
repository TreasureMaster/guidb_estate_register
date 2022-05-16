import tkinter as tk


class ScrolledListboxFrame(tk.Frame):

    def __init__(self, master, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)
        self._make_widgets()

    def _make_widgets(self):
        # Для прокрутки окна со значениями вводим Scrollbar (если значений больше, чем размер таблицы)
        sbar = tk.Scrollbar(self)
        self.listbox = tk.Listbox(self, width=50)
        sbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sbar.set)
        sbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    def add_list(self, lb_list):
        """Добавить список в Listbox и зарегистрировать в реестре, если нужно."""
        itemlist = tk.StringVar(value=lb_list)
        self.listbox.config(
            listvariable=itemlist
        )

    def set_command(self, command):
        """Установить команду обработки выбора строки в списке."""
        self.listbox.bind('<<ListboxSelect>>', command)