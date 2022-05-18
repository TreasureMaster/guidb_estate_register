import tkinter as tk
from tkinter.messagebox import showwarning
import win32api
import win32print
import tempfile

from widgets import ScrolledListboxFrame, PrinterOrientationRadioBox
# class ScrolledListboxFrame(tk.Frame):

#     def __init__(self, master, cnf={}, **kwargs):
#         super().__init__(master, cnf, **kwargs)
#         self._make_widgets()

#     def _make_widgets(self):
#         # Для прокрутки окна со значениями вводим Scrollbar (если значений больше, чем размер таблицы)
#         sbar = tk.Scrollbar(self)
#         self.listbox = tk.Listbox(self, width=50)
#         sbar.config(command=self.listbox.yview)
#         self.listbox.config(yscrollcommand=sbar.set)
#         sbar.pack(side=tk.RIGHT, fill=tk.Y)
#         self.listbox.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

#     def add_list(self, lb_list):
#         """Добавить список в Listbox и зарегистрировать в реестре, если нужно."""
#         itemlist = tk.StringVar(value=lb_list)
#         self.listbox.config(
#             listvariable=itemlist
#         )

#     def set_command(self, command):
#         """Установить команду обработки выбора строки в списке."""
#         self.listbox.bind('<<ListboxSelect>>', command)


class PrinterDialog(tk.Toplevel):
    """Окно диалога печати"""
    _APPTITLE = 'Печать'
    # родительский виджет сохраняется в self.master
    def __init__(self, master=None, cnf={}, **kw):
        self.current_printer = None
        self.print_filename = kw.pop('print_text', cnf.pop('print_text', ''))
        super().__init__(master, cnf, **kw)
        self.title(self._APPTITLE)
        self.protocol('WM_DELETE_WINDOW', self._quit)

        self._make_widgets()

        self.focus_set()
        self.grab_set()
        self.wait_window()

    def _make_widgets(self):
        """."""
        main_frame = tk.Frame(self)
        main_frame.pack(expand=tk.YES, fill=tk.BOTH)

        # tk.Label(main_frame, text='Общие настройки', anchor=tk.W).pack(padx=10, pady=10, fill=tk.X)
        printer_frame = tk.LabelFrame(main_frame, text='Выбор принтера')
        printer_frame.pack(fill=tk.BOTH, padx=20, pady=5)

        self.listbox = ScrolledListboxFrame(printer_frame)
        self.listbox.pack(fill=tk.BOTH, padx=5, pady=5)
        self.listbox.add_list(self.get_printers())
        self.listbox.set_command(self.set_printer)

        setup_frame = tk.LabelFrame(main_frame, text='Настройки принтера')
        setup_frame.pack(fill=tk.BOTH, padx=20, pady=5)
        self.orientation = PrinterOrientationRadioBox(setup_frame)
        self.orientation.set(1)
        self.orientation.pack()

        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(btn_frame, text='Применить', command=self.set_printer).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text='Отмена', command=self._quit).pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text='Печать', command=self.do_print).pack(side=tk.RIGHT, padx=5)

    def _quit(self):
        """Собственная обработка выхода."""
        # self.mainwindow.deiconify()
        self.destroy()

    def get_printers(self):
        """Получить принтеры системы."""
        return [
            p[2] for p in win32print.EnumPrinters(2)
        ]

    def set_printer(self, event=None):
        """Выбор принтера для печати."""
        if event is not None:
            self.current_printer = event.widget.get(event.widget.curselection())
            # print(f'Принтер: {self.current_printer}')
        elif not self.current_printer:
            showwarning('Выбор принтера', 'Выберите принтер!')
        # else:
        #     print(f'Принтер: {self.current_printer}')

    def do_print(self):
        PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
        pHandle = win32print.OpenPrinter(self.current_printer, PRINTER_DEFAULTS)
        properties = win32print.GetPrinter(pHandle, 2)
        properties['pDevMode'].Orientation = self.orientation.get()
        win32print.SetPrinter(pHandle, 2, properties, 0)
        # filename = tempfile.mkstemp(suffix='.txt', dir='temp_files', text=True)[1]
        # print('---> filename:', filename)
        # open(filename, "w").write(self.print_filename)
        try:
            win32api.ShellExecute(
                0,
                "printto",
                self.print_filename,
                # "requirements.txt",
                '"%s"' % self.current_printer,
                ".",
                0
            )
        finally:
            win32print.ClosePrinter(pHandle)
        # os.remove(filename)


if __name__ == '__main__':
    root = tk.Tk()
    tk.Label(root, text='Тестирование печати в принтер').pack(padx=10, pady=10)
    tk.Button(root, text='Печать', command=lambda master=root: PrinterDialog(master)).pack(padx=10, pady=10)

    root.mainloop()