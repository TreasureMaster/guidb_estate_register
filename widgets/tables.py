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


class TreatyTable(BaseTable):
    """Таблица договоров"""
    _HEADERS = (
        'Номер', 'Начало действия', 'Окончание', 'Дата подписания',
        'Изготовление', 'Стоимость работы', 'Стоимость аренды', 'Период оплаты',
        'Ответственный', 'Номер щита', 'Арендатор'
    )
    _ALIGN = ('c', 'r', 'r', 'r', 'l', 'l')
    _INDEXES = {
        '#1': 'IDTreaty',
        '#2': 'DateStart',
        '#3': 'StopDate',
        '#4': 'SignDate',
        '#5': 'Advertisement',
        '#6': 'Cost',
        '#7': 'Leasing',
        '#8': 'Period',
        '#9': 'Employee',
        '#10': 'BillboardID',
        '#11': 'Customer',
    }
    # Атрибуты вида колонок
    _COLUMNS = {
        '#1': {'width': 70, 'anchor': tk.CENTER},
        '#2': {'width': 120, 'anchor': tk.E},
        '#3': {'width': 90, 'anchor': tk.E},
        '#4': {'width': 120, 'anchor': tk.E},
        '#5': {'width': 100, 'anchor': tk.E},
        '#6': {'width': 120, 'anchor': tk.E},
        '#7': {'width': 130, 'anchor': tk.E},
        '#8': {'width': 110, 'anchor': tk.E},
        '#9': {'width': 100, 'anchor': tk.E},
        '#10': {'width': 90, 'anchor': tk.CENTER},
        '#11': {'width': 110, 'anchor': tk.E},
    }
    # Отображение полей БД в человекочитаемом виде
    _DISPLAY_FIELDS = {
        'Advertisement': {
            False: 'нет',
            True: 'да',
        },
        # 'Comment': {
        #     None: 'нет',
        #     '': 'нет',
        #     '!display_field': 'да',
        # },
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


class CustomerTable(BaseTable):
    _HEADERS = (
        'ИНН', 'Статус', 'Арендатор', 'Адрес',
        'Банк', 'Номер счета', 'Налоговая',
        'Руководитель', 'Телефон'
    )
    _INDEXES = {
            '#1': 'INN',
            '#2': 'Status',
            '#3': 'Customer',
            '#4': 'AddressCust',
            '#5': 'Bank',
            '#6': 'Account',
            '#7': 'Tax',
            '#8': 'Chief',
            '#9': 'Phone',
        }
    _COLUMNS = {
        '#1': {'width': 70, 'anchor': tk.E},
        '#2': {'width': 50, 'anchor': tk.E},
        '#3': {'width': 110},
        # '#4': {'width': 110, 'anchor': tk.E},
        '#5': {'width': 120},
        '#6': {'width': 130, 'anchor': tk.E},
        '#9': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class EmployeeTable(BaseTable):
    _HEADERS = ('Ответственный',)
    _INDEXES = {
            '#1': 'Employee',
        }
    _COLUMNS = {
        # '#1': {'width': 200, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {}


class PeriodTable(BaseTable):
    _HEADERS = ('Период оплаты',)
    _INDEXES = {
            '#1': 'Period',
        }
    _COLUMNS = {}
    _DISPLAY_FIELDS = {}


class BillboardTable(BaseTable):
    _HEADERS = (
        'Адрес установки', 'Местоположение', 'Площадь щита',
        'Район', 'Размеры', 'Картинка',
    )
    _INDEXES = {
            '#1': 'Address',
            '#2': 'Orientation',
            '#3': 'Square',
            '#4': 'District',
            '#5': 'Size',
            '#6': 'Picture',
        }
    _COLUMNS = {
        # '#1': {'width': 110},
        '#2': {'width': 120, 'anchor': tk.E},
        '#3': {'width': 110, 'anchor': tk.E},
        '#4': {'width': 120},
        '#5': {'width': 80, 'anchor': tk.E},
        '#6': {'width': 80, 'anchor': tk.E},
    }
    _DISPLAY_FIELDS = {
        # 'SignPhone': {
        #     False: 'нет',
        #     True: 'да',
        # },
        # 'Privat': {
        #     False: 'нет',
        #     True: 'да',
        # },
        # 'Comment': {
        #     None: '',
        # },
        # 'Seller': {
        #     None: '',
        # },
        # 'Back': {
        #     None: '',
        # },
        # 'BackSum': {
        #     None: '',
        # },
        # 'FreeThing': {
        #     None: '',
        # },
        # 'Price': {
        #     None: '',
        # },
        'Picture': {
            None: 'нет',
            '': 'нет',
            '!display_field': 'есть',
        },
    }
