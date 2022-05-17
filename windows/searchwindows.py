import tempfile
import tkinter as tk

from prettytable import PrettyTable

from widgets import (
    AdminTable,
    LabeledEntry,
    ToggledEntry,
    # TreatyTable,
)

from .printerwindow import PrinterDialog


class BaseSearchWindow:
    """Базовое окно поиска"""

    def __init__(self, parent, model):
        self.parent = parent
        self.model = model
        self.data = {}
        self.window = tk.Toplevel(self.parent.mainwindow)
        self.window.title(self._APPTITLE)
        self.window.protocol('WM_DELETE_WINDOW', self._quit)

        self._make_widgets()

        self.window.focus_set()
        self.window.grab_set()
        self.window.wait_window()

    def _make_widgets(self):
        control_frame = tk.Frame(self.window)
        control_frame.pack(side=tk.LEFT, pady=10)

        users_frame = tk.Frame(self.window)
        users_frame.pack(expand=tk.YES, fill=tk.BOTH)
        self.model_table = self._TABLE(users_frame, table_model=self.model)
        self.model_table.pack(expand=tk.YES, fill=tk.BOTH)

        for field, widget in self._CONTROL_WIDGETS.items():
            if field.startswith('!button'):
                tk.Button(
                    control_frame,
                    text=widget['text'],
                    command=getattr(self, widget['command']),
                    width=self._ALL_WIDTH
                ).pack(padx=15, pady=widget['height'])
            elif field.startswith('!separator'):
                tk.Label(control_frame, text='').pack(pady=widget)
            else:
                entry = widget['widget'](control_frame, text=widget['text'], entry_width=self._ALL_WIDTH)
                entry.pack()
                self.data[field] = entry

    def _quit(self):
        """Собственная обработка выхода."""
        # self.mainwindow.deiconify()
        self.window.destroy()

    def search_table(self):
        """Вывести найденные значения полей"""
        self.model_table.tree.delete(*self.model_table.tree.get_children())
        search_keys = {key: value.get() for key, value in self.data.items() if value.get()}
        if not search_keys:
            rows = self.model.select_all()
        else:
            rows = self.model.select_likes(search_keys)

        for row in rows:
            self.model_table.fill_row(row)

    def create_report(self):
        """Создать отчет"""
        pass

    def get_print_file(self):
        """Сохранить временный csv-файл."""
        pt = PrettyTable()
        pt.field_names = self.model_table._HEADERS
        for column, align in zip(self.model_table._HEADERS, self.model_table._ALIGN):
            pt.align[column] = align
        for row_id in self.model_table.tree.get_children():
                row = (self.model_table.tree.item(row_id)['values'])
                # if isinstance(self.model_table, TreatyTable):
                #     row.insert(4, '{0[0]} {0[1]:.1}.{0[2]:.1}.'.format(
                #         row.pop(4).split()
                #     ))
                pt.add_row(row)
        self.temp_filename = tempfile.mkstemp(suffix='.txt', dir='temp_files', text=True)[1]
        with open(self.temp_filename, 'w', encoding='utf-8') as fd:
            fd.write(pt.get_string())

        return self.temp_filename


class TreatySearchWindow(BaseSearchWindow):
    """Окно поиска договора"""
    _APPTITLE = 'Поиск договора'
    # _TABLE = TreatyTable
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
            'customer.Customer': {
                'text': 'По арендатору',
                'widget': ToggledEntry
            },
            'employees.Employee': {
                'text': 'По ответственному',
                'widget': ToggledEntry
            },
            '!separator_1': 5,
            '!button_1': {
                'text': 'Поиск',
                'height': 10,
                'command': 'search_table'
            },
            '!button_2': {
                'text': 'Отчет',
                'height': 0,
                'command': 'create_report'
            },
            '!separator_2': 10,
            '!button_3': {
                'text': 'Отмена',
                'height': 20,
                'command': '_quit'
            },
        }

    def create_report(self):
        """Создать отчет"""
        PrinterDialog(self.window, print_text=self.get_print_file())
        # try:
        #     os.remove(self.temp_filename)
        # except Exception:
        #     pass



class AdminSearchWindow(BaseSearchWindow):
    """Окно поиска пользователя"""
    _APPTITLE = 'Поиск пользователя'
    _TABLE = AdminTable
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
            'Login': {
                'text': 'По логину:',
                'widget': LabeledEntry
            },
            '!separator_1': 10,
            '!button_1': {
                'text': 'Поиск',
                'height': 10,
                'command': 'search_table'
            },
            '!button_2': {
                'text': 'Отчет',
                'height': 0,
                'command': 'create_report'
            },
            '!separator_2': 10,
            '!button_3': {
                'text': 'Отмена',
                'height': 20,
                'command': '_quit'
            },
        }

    def create_report(self):
        """Создать отчет"""
        PrinterDialog(self.window, print_text=self.get_print_file())
        # try:
        #     os.remove(self.temp_filename)
        # except Exception as e:
        #     print(e)