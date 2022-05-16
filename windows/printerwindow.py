import tkinter as tk
from tkinter.messagebox import showwarning
import win32api
import win32print
import tempfile

from widgets import ScrolledListboxFrame


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

        tk.Label(main_frame, text='Общие настройки', anchor=tk.W).pack(padx=10, pady=10, fill=tk.X)
        printer_frame = tk.LabelFrame(main_frame, text='Выберите принтер')
        printer_frame.pack(fill=tk.BOTH, padx=20)

        self.listbox = ScrolledListboxFrame(printer_frame)
        self.listbox.pack(fill=tk.BOTH, padx=5, pady=5)
        self.listbox.add_list(self.get_printers())
        self.listbox.set_command(self.set_printer)

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
        # filename = tempfile.mkstemp(suffix='.txt', dir='temp_files', text=True)[1]
        # print('---> filename:', filename)
        # open(filename, "w").write(self.print_filename)
        win32api.ShellExecute(
            0,
            "printto",
            self.print_filename,
            '"%s"' % self.current_printer,
            ".",
            0
        )
        # os.remove(filename)


if __name__ == '__main__':
    root = tk.Tk()
    tk.Label(root, text='Тестирование печати в принтер').pack(padx=10, pady=10)
    tk.Button(root, text='Печать', command=lambda master=root: PrinterDialog(master)).pack(padx=10, pady=10)

    root.mainloop()