import tkinter as tk
import tkinter.ttk as ttk

from tkinter.messagebox import showwarning


class BaseTable(tk.Frame):

    def __init__(self, master, cnf={}, **kwargs):
        # Модель таблицы БД из models
        self.table_model = kwargs.pop(
            'table_model', cnf.pop('table_model', None)
        )
        # Список всех строк из таблицы
        self.inner_table = self.get_users()
        self.current_entry = None
        super().__init__(master, cnf, **kwargs)

        if self.inner_table:
            self._create_table()

    def get_users(self):
        return self.table_model.select_all()

    def _create_table(self):
        """Создание таблицы договоров"""
        self.tree = ttk.Treeview(
            self, show='headings',
            columns=self._INDEXES.keys()
        )
        for idx, title in zip(self._INDEXES.keys(), self._HEADERS):
            self.tree.heading(idx, text=title)

        self.ysb = ttk.Scrollbar(
            self, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscroll=self.ysb.set)

        for params in self.inner_table:
            self.fill_row(params)

        self.column_width_setup()

        self.tree.bind('<<TreeviewSelect>>', self.choose_selection)

        self.tree.grid(row=0, column=0)
        self.ysb.grid(row=0, column=1, sticky=(tk.N + tk.S))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.delete()

    def fill_row(self, row):
        """Заполнить строку таблицы"""
        self.tree.insert(
                '', tk.END,
                # виртуальный номер строки (удобно задать по ключу параметра)
                iid=row[self.table_model._primary_key],
                values=[
                    self.get_viewed_field(column, row[column])
                    for column in self._INDEXES.values()
                ]
            )

    def get_viewed_field(self, column, field):
        """Человекочитаемое отображение поля"""
        if props := self._DISPLAY_FIELDS.get(column):
            if (viewed := props.get(field)) is not None:
                return viewed
            elif (viewed := props.get('!display_field')) is not None:
                return viewed
        return field

    def choose_selection(self, event):
        for selection in self.tree.selection():
            self.current_entry = selection

    def update_cell(self, row):
        """Изменение значения ячейки при редактировании записи в таблице"""
        for num, name in self._INDEXES.items():
            if name == 'is_admin':
                self.tree.set(
                    row[self.table_model._primary_key], num, 'администратор'
                    if row['is_admin'] else 'пользователь'
                )
            else:
                self.tree.set(
                    row[self.table_model._primary_key], num, row[name]
                )

    def delete_entry(self):
        """Удалить пользователя"""
        if self.current_entry is None:
            showwarning(
                'Удаление записи',
                'Не выбран пользователь для удаления'
            )
        else:
            self.tree.delete(self.current_entry)
            self.table_model.delete(self.current_entry)
            self.current_entry = None

    def column_width_setup(self):
        """Установить вид колонок (ширина и выравнивание)"""
        for index, attrs in self._COLUMNS.items():
            self.tree.column(index, **attrs)


# ------------------- Описание конкретных таблиц приложения ------------------ #
# Описание атрибутов классов:
# _HEADERS - заголовки таблицы в порядке их вывода на экран
# _ALIGN - выравнивание данных в ячейках таблиц (только для печати)
# _INDEXES - порядок ввода данных
# (ключ - индекс-колонка положения в таблице, значение - название поля БД или композитного свойства)

# Примечание: композитное свойство - это значение, созданное из нескольких полей.
# Эти данные должны вводиться в порядке их вывода на экран. Их кол-во также должно совпадать.


class BuildingTable(BaseTable):
    """Таблица зданий"""
    _HEADERS = (
        'Название', 'Площадь', 'Адрес', 'Год постройки',
        'Материал', 'Износ', 'Этажей', 'Фото',
        'Информация',
    )
    # _ALIGN = ('c', 'r', 'r', 'r', 'l', 'l')
    _INDEXES = {
        '#1': 'BuildingName',
        '#2': 'Land',
        '#3': 'Address',
        '#4': 'Year',
        '#5': 'MaterialID',
        '#6': 'Wear',
        '#7': 'Flow',
        '#8': 'Picture',
        '#9': 'Comment',
    }
    # Атрибуты вида колонок
    _COLUMNS = {
        # '#1': {'width': 70, 'anchor': tk.CENTER},
        # '#2': {'width': 120, 'anchor': tk.E},
        # '#3': {'width': 90, 'anchor': tk.E},
        # '#4': {'width': 120, 'anchor': tk.E},
        # '#5': {'width': 100, 'anchor': tk.E},
        # '#6': {'width': 120, 'anchor': tk.E},
        # '#7': {'width': 130, 'anchor': tk.E},
        # '#8': {'width': 110, 'anchor': tk.E},
        # '#9': {'width': 100, 'anchor': tk.E},
    }
    # Отображение полей БД в человекочитаемом виде
    _DISPLAY_FIELDS = {
        # 'Advertisement': {
        #     False: 'нет',
        #     True: 'да',
        # },
        'Picture': {
            None: 'нет',
            '': 'нет',
            '!display_field': 'да',
        },
        'Comment': {
            None: 'нет',
            '': 'нет',
            '!display_field': 'да',
        },
    }


class AdminTable(BaseTable):
    _HEADERS = ('Номер', 'Логин', 'Роль')
    _ALIGN = ('r', 'r', 'r')
    _INDEXES = {
            '#1': 'IDUser',
            '#2': 'Login',
            '#3': 'is_admin'
        }
    _COLUMNS = {}
    _DISPLAY_FIELDS = {
        'is_admin': {
            False: 'пользователь',
            True: 'администратор',
        },
    }


class DepartmentTable(BaseTable):
    _HEADERS = (
        'Название', 'Заведующий', 'Телефон', 'Деканат',
    )
    _INDEXES = {
            '#1': 'departmentName',
            '#2': 'Boss',
            '#3': 'Phone',
            '#4': 'OfficeDean',
        }
    _COLUMNS = {
        # '#1': {'width': 70, 'anchor': tk.E},
        # '#2': {'width': 50, 'anchor': tk.E},
        # '#3': {'width': 110},
        # '#4': {'width': 110, 'anchor': tk.E},
        # '#5': {'width': 120},
        # '#6': {'width': 130, 'anchor': tk.E},
        # '#9': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class MaterialTable(BaseTable):
    _HEADERS = ('Материал',)
    _INDEXES = {
            '#1': 'Material',
        }
    _COLUMNS = {
        # '#1': {'width': 200, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class TargetTable(BaseTable):
    _HEADERS = ('Назначение помещения',)
    _INDEXES = {
            '#1': 'Target',
        }
    _COLUMNS = {}
    _DISPLAY_FIELDS = {}


class HallTable(BaseTable):
    _HEADERS = (
        'Номер', 'Площадь', 'Окна',
        'Батареи', 'Кафедра', 'Здание',
    )
    _INDEXES = {
            '#1': 'HallNumber',
            '#2': 'HallSquare',
            '#3': 'Windows',
            '#4': 'Heaters',
            '#5': 'DepartmentID',
            '#6': 'KadastrID',
        }
    _COLUMNS = {
        # '#1': {'width': 110},
        # '#2': {'width': 120, 'anchor': tk.E},
        # '#3': {'width': 110, 'anchor': tk.E},
        # '#4': {'width': 120},
        # '#5': {'width': 80, 'anchor': tk.E},
        # '#6': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class UnitTable(BaseTable):
    _HEADERS = (
        'Название', 'Дата постановки', 'Стоимость',
        'Год переоценки', 'Цена списания', 'Срок службы',
        'Помещение', 'Ответственный',
    )
    _INDEXES = {
            '#1': 'UnitName',
            '#2': 'DateStart',
            '#3': 'Cost',
            '#4': 'CostYear',
            '#5': 'CostAfter',
            '#6': 'Period',
            '#7': 'HallID',
            '#8': 'ChiefID',
        }
    _COLUMNS = {
        # '#1': {'width': 110},
        # '#2': {'width': 120, 'anchor': tk.E},
        # '#3': {'width': 110, 'anchor': tk.E},
        # '#4': {'width': 120},
        # '#5': {'width': 80, 'anchor': tk.E},
        # '#6': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class ChiefTable(BaseTable):
    _HEADERS = (
        'Фамилия', 'Адрес', 'Годы опыта',
    )
    _INDEXES = {
            '#1': 'Chief',
            '#2': 'AddressChief',
            '#3': 'Experience',
        }
    _COLUMNS = {
        # '#1': {'width': 110},
        # '#2': {'width': 120, 'anchor': tk.E},
        # '#3': {'width': 110, 'anchor': tk.E},
        # '#4': {'width': 120},
        # '#5': {'width': 80, 'anchor': tk.E},
        # '#6': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}
