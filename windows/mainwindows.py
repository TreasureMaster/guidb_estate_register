import tkinter as tk
import tempfile

from prettytable import PrettyTable

from models import (
    PGCursor,
    BuildingModel,
    ChiefModel,
    DepartmentModel,
    HallModel,
    MaterialModel,
    TargetModel,
    UnitModel,
    UserModel,
)
from widgets import (
    AdminTable,
    BuildingTable,
    ChiefTable,
    DepartmentTable,
    HallTable,
    MaterialTable,
    TargetTable,
    UnitTable,
)
from .editwindows import (
    AdminEditWindow,
    BuildingEditWindow,
    ChiefEditWindow,
    DepartmentEditWindow,
    HallEditWindow,
    UnitEditWindow,
)
from .searchwindows import TreatySearchWindow, AdminSearchWindow
from .printerwindow import PrinterDialog


class BaseMainWindow:
    """Базовое главное окно"""
    def __init__(self, mainwindow, table_model=None):
        self.mainwindow = mainwindow
        self.mainwindow.withdraw()
        self.model = self._MODEL(PGCursor()) if table_model is None else table_model
        self.returned_entry = None
        self.data = {}
        self.window = tk.Toplevel(self.mainwindow)
        self.window.title(self._APPTITLE)
        self.window.protocol('WM_DELETE_WINDOW', self._quit)
        # super().__init__()
        self._make_widgets()

        self.window.focus_set()
        self.window.grab_set()
        self.window.wait_window()

    def _quit(self):
        """Собственная обработка выхода."""
        self.mainwindow.deiconify()
        self.window.destroy()

    def _makemenu(self, parent):
        """."""

    def _make_widgets(self):
        self._makemenu(self.window)
        control_frame = tk.Frame(self.window)
        control_frame.pack(side=tk.LEFT)

        table_frame = tk.Frame(self.window)
        table_frame.pack(expand=tk.YES, fill=tk.BOTH)
        self.model_table = self._TABLE(table_frame, table_model=self.model)
        self.model_table.pack(expand=tk.YES, fill=tk.BOTH)

        for field, widget in self._CONTROL_WIDGETS.items():
            if field.startswith('!button'):
                tk.Button(
                    control_frame,
                    text=widget['text'],
                    command=getattr(self, widget['command']),
                    width=self._ALL_WIDTH
                ).pack(padx=15, pady=widget['pady'])
            elif field.startswith('!separator'):
                tk.Label(control_frame, text='').pack(pady=widget)
            else:
                entry = widget['widget'](control_frame, text=widget['text'], entry_width=self._ALL_WIDTH)
                entry.pack()
                self.data[field] = entry

    def create_entry(self):
        """Открыть окно добавления/редактирования контракта"""
        self._EDIT_WINDOW(self, self.model)
        if self.returned_entry is not None:
            self.model_table.fill_row(self.returned_entry)
            self.model_table.current_entry = None

    def update_entry(self):
        """Открыть окно добавления/редактирования контракта"""
        self._EDIT_WINDOW(self, self.model, self.model_table.current_entry)
        if self.returned_entry is not None:
            self.model_table.update_cell(self.returned_entry)
            # self.model_table.current_entry = None

    def delete_entry(self):
        """Удалить запись"""
        self.model_table.delete_entry()

    def search_entry(self):
        """Поиск контракта"""
        if self._SEARCH_WINDOW is not None:
            self._SEARCH_WINDOW(self, self.model)

    def create_report(self):
        """Создать отчет"""
        pass

    def get_print_file(self):
        """Сохранить временный текстовый файл."""
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


class BuildingMainWindow(BaseMainWindow):
    """Базовое окно зданий"""
    _APPTITLE = 'Здания'
    _MODEL = BuildingModel
    _TABLE = BuildingTable
    _EDIT_WINDOW = BuildingEditWindow
    # _SEARCH_WINDOW = TreatySearchWindow
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
            '!button_1': {
                'text': 'Кафедры',
                'pady': 0,
                'command': 'departments_view'
            },
            '!button_2': {
                'text': 'Аудитории',
                'pady': 0,
                'command': 'halls_view'
            },
            '!button_3': {
                'text': 'Имущество',
                'pady': 0,
                'command': 'units_view'
            },
            '!button_4': {
                'text': 'Ответственные',
                'pady': 0,
                'command': 'chiefs_view'
            },
            '!separator_1': 10,
            '!button_5': {
                'text': 'Добавить',
                'pady': 0,
                'command': 'create_entry'
            },
            '!button_6': {
                'text': 'Изменить',
                'pady': 20,
                'command': 'update_entry'
            },
            '!button_7': {
                'text': 'Удалить',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!separator_2': 10,
            '!button_8': {
                'text': 'Поиск',
                'pady': 0,
                'command': 'search_entry'
            },
            '!button_9': {
                'text': 'Отчет',
                'pady': 10,
                'command': 'create_report'
            },
        }

    # def _quit(self):
    #     """Собственная обработка выхода."""
    #     self.mainwindow.deiconify()
    #     self.window.destroy()

    def _makemenu(self, parent):
        # win - окно верхнего уровня
        top = tk.Menu(parent)
        # установить его параметры menu
        parent.config(menu=top)

        tables = tk.Menu(top, tearoff=False)
        tables.add_command(label='Материал стен', command=self.materials_view, underline=0)
        tables.add_command(label='Назначение помещения', command=self.targets_view, underline=0)
        tables.add_separator()
        tables.add_command(label='Выход', command=self._quit, underline=0)
        top.add_cascade(label='Справочные таблицы', menu=tables, underline=0)

    def departments_view(self):
        """Переключение на таблицу кафедр"""
        # self.window.withdraw()
        DepartmentMainWindow(self.window)

    def halls_view(self):
        """Переключение на таблицу помещений"""
        HallMainWindow(self.window)

    def units_view(self):
        """Переключение на таблицу имущества"""
        UnitMainWindow(self.window)

    def chiefs_view(self):
        """Переключение на таблицу ответственных"""
        ChiefMainWindow(self.window)

    def materials_view(self):
        """Переключение на таблицу материалов стен"""
        MaterialMainWindow(self.window)

    def targets_view(self):
        """Переключение на таблицу назначения помещения"""
        TargetMainWindow(self.window)

    def create_report(self):
        """Создать отчет"""
        PrinterDialog(self.window, print_text=self.get_print_file())


class AdminMainWindow(BaseMainWindow):
    """Базовое окно пользователей"""
    _APPTITLE = 'Администратор'
    _MODEL = UserModel
    _TABLE = AdminTable
    _EDIT_WINDOW = AdminEditWindow
    _SEARCH_WINDOW = AdminSearchWindow
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
            '!button_1': {
                'text': 'Добавить пользователя',
                'pady': 10,
                'command': 'create_entry'
            },
            '!button_2': {
                'text': 'Удалить пользователя',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!button_3': {
                'text': 'Редактировать',
                'pady': 20,
                'command': 'update_entry'
            },
            '!separator_1': 10,
            '!button_4': {
                'text': 'Поиск',
                'pady': 0,
                'command': 'search_entry'
            },
            '!button_5': {
                'text': 'Отчет',
                'pady': 10,
                'command': 'create_report'
            },
        }

    # def _quit(self):
    #     """Собственная обработка выхода."""
    #     self.mainwindow.deiconify()
    #     self.window.destroy()

    def create_report(self):
        """Создать отчет"""
        PrinterDialog(self.window, print_text=self.get_print_file())


class DepartmentMainWindow(BaseMainWindow):
    """Базовое окно кафедр"""
    _APPTITLE = 'Кафедра'
    _MODEL = DepartmentModel
    _TABLE = DepartmentTable
    _EDIT_WINDOW = DepartmentEditWindow
    # _SEARCH_WINDOW = RouteSearchWindow
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        '!separator_1': 10,
            '!button_1': {
                'text': 'Добавить',
                'pady': 10,
                'command': 'create_entry'
            },
            '!button_2': {
                'text': 'Изменить',
                'pady': 20,
                'command': 'update_entry'
            },
            '!button_3': {
                'text': 'Удалить',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!separator_2': 10,
            '!button_5': {
                'text': 'Выход',
                'pady': 10,
                'command': '_quit'
            },
        }


class HallMainWindow(BaseMainWindow):
    """Базовое окно помещения"""
    _APPTITLE = 'Помещение'
    _MODEL = HallModel
    _TABLE = HallTable
    _EDIT_WINDOW = HallEditWindow
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        '!separator_1': 10,
            '!button_1': {
                'text': 'Добавить',
                'pady': 10,
                'command': 'create_entry'
            },
            '!button_2': {
                'text': 'Изменить',
                'pady': 20,
                'command': 'update_entry'
            },
            '!button_3': {
                'text': 'Удалить',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!separator_2': 10,
            '!button_5': {
                'text': 'Выход',
                'pady': 10,
                'command': '_quit'
            },
        }


class UnitMainWindow(BaseMainWindow):
    """Базовое окно имущеста"""
    _APPTITLE = 'Имущество'
    _MODEL = UnitModel
    _TABLE = UnitTable
    _EDIT_WINDOW = UnitEditWindow
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        '!separator_1': 10,
            '!button_1': {
                'text': 'Добавить',
                'pady': 10,
                'command': 'create_entry'
            },
            '!button_2': {
                'text': 'Изменить',
                'pady': 20,
                'command': 'update_entry'
            },
            '!button_3': {
                'text': 'Удалить',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!separator_2': 10,
            '!button_5': {
                'text': 'Выход',
                'pady': 10,
                'command': '_quit'
            },
        }


class ChiefMainWindow(BaseMainWindow):
    """Базовое окно ответственных"""
    _APPTITLE = 'Ответственные за имущество'
    _MODEL = ChiefModel
    _TABLE = ChiefTable
    _EDIT_WINDOW = ChiefEditWindow
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        '!separator_1': 10,
            '!button_1': {
                'text': 'Добавить',
                'pady': 10,
                'command': 'create_entry'
            },
            '!button_2': {
                'text': 'Изменить',
                'pady': 20,
                'command': 'update_entry'
            },
            '!button_3': {
                'text': 'Удалить',
                'pady': 0,
                'command': 'delete_entry'
            },
            '!separator_2': 10,
            '!button_5': {
                'text': 'Выход',
                'pady': 10,
                'command': '_quit'
            },
        }


class MaterialMainWindow(BaseMainWindow):
    """Справочное окно материалов здания"""
    _APPTITLE = 'Справочная таблица "Материал здания"'
    _MODEL = MaterialModel
    _TABLE = MaterialTable
    _EDIT_WINDOW = None
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        # '!separator_1': 10,
        # '!button_1': {
        #     'text': 'Добавить',
        #     'pady': 10,
        #     'command': 'create_entry'
        # },
        # '!button_2': {
        #     'text': 'Удалить',
        #     'pady': 0,
        #     'command': 'delete_entry'
        # },
        # '!button_3': {
        #     'text': 'Изменить',
        #     'pady': 20,
        #     'command': 'update_entry'
        # },
        # '!separator_2': 10,
        '!button_1': {
            'text': 'Выход',
            'pady': 10,
            'command': '_quit'
        },
    }


class TargetMainWindow(BaseMainWindow):
    """Справочное окно назначения помещения"""
    _APPTITLE = 'Справочная таблица "Назначение помещения"'
    _MODEL = TargetModel
    _TABLE = TargetTable
    _EDIT_WINDOW = None
    _SEARCH_WINDOW = None
    _ALL_WIDTH = 25
    _CONTROL_WIDGETS = {
        # '!separator_1': 10,
            # '!button_1': {
            #     'text': 'Добавить',
            #     'pady': 10,
            #     'command': 'create_entry'
            # },
            # '!button_2': {
            #     'text': 'Удалить',
            #     'pady': 0,
            #     'command': 'delete_entry'
            # },
            # '!button_3': {
            #     'text': 'Изменить',
            #     'pady': 20,
            #     'command': 'update_entry'
            # },
            # '!separator_2': 10,
            '!button_1': {
                'text': 'Выход',
                'pady': 10,
                'command': '_quit'
            },
        }
