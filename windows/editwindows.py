import tkinter as tk
import tkinter.ttk as ttk

from tkinter.messagebox import showerror, showinfo
from tkcalendar import DateEntry

from widgets import (
    BaseCustomEntry,
    ButtonsBox,
    CheckbuttonEntry,
    ComboboxDict,
    IdEntry,
    FilenameEntry,
    ModuleImage,
    RadioBox,
)
from extras import identify_error, collect_message


class BaseEditWindow:
    """Базовое окно редактирования"""
    _WITH_PICTURE = False
    def __init__(self, parent, table_model, current_entry=None):
        self.parent = parent
        self.model = table_model
        # Текущий id записи
        self.current_entry = current_entry
        # Считать всю запись для редактирования
        if self.current_entry is not None:
            self.current_object = self.model.select_by_id(self.current_entry)
        else:
            self.current_object = None
        self.data = {}
        self.window = tk.Toplevel(self.parent.mainwindow)
        self.window.title(self._APPTITLE)
        self.window.protocol('WM_DELETE_WINDOW', self._quit)

        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(expand=tk.YES, fill=tk.BOTH, padx=30, pady=30)
        self._make_widgets()

        self.window.focus_set()
        self.window.grab_set()
        self.window.wait_window()

    def _make_widgets(self):
        """Создание виджетов окна"""
        for row, (field, item) in enumerate(self._ROWS_LIST.items(), start=1):
            # последние кнопки
            if field == '!buttons_frame':
                if self._WITH_PICTURE:
                    row += 1
                tk.Button(
                    self.main_frame, text='OK',
                    command=self.set_contract,
                    width=10
                ).grid(row=row, column=0, padx=10, pady=10, sticky=tk.E)
                tk.Button(
                    self.main_frame, text='Отмена',
                    command=self._quit,
                    width=10
                ).grid(row=row, column=1, padx=10, pady=10)
                continue
            # Метки и поля ввода/выбора
            tk.Label(self.main_frame, text=item['title'], width=22, anchor=tk.W).grid(row=row, column=0)
            if field in self._COMBO_LIST.keys():
                entry = ComboboxDict(
                    self.main_frame,
                    values=getattr(self, self._COMBO_LIST[field])(),
                    width=27, state='readonly'
                )
                if self.current_object is not None:
                    entry.current(
                        entry.get_keys().index(self.current_object[field])
                    )
            else:
                entry = item['widget'](self.main_frame, **item['widget_attrs'])
                if isinstance(entry, ttk.Spinbox):
                    entry.configure(width=10, from_=1, to=100, state='readonly')
                    entry.set(1)
                if self.current_object is not None and field != 'Password':
                    if isinstance(entry, DateEntry):
                        entry.set_date(self.current_object[field])
                    elif isinstance(
                        entry,
                        (RadioBox, ButtonsBox, BaseCustomEntry)
                    ):
                        entry.set(self.current_object[field])
                    elif isinstance(entry, ttk.Spinbox):
                        entry.set(self.current_object[field])
                        if field == 'Floor':
                            entry.configure(to=self.current_object['Floors'])
                    else:
                        entry.insert(
                            0,
                            (
                                res
                                if (res := self.current_object[field]) is not None
                                else ''
                            )
                        )
            entry.grid(row=row, column=1, padx=10, pady=10, sticky=tk.W)
            self.data[field] = entry

    def _quit(self):
        """Собственная обработка выхода."""
        self.window.destroy()

    def set_contract(self):
        """Создание нового или обновление существующей записи"""
        title = f'{self._SHOWTITLE}: ошибка работы'
        update_data = {key: entry.get() for key, entry in self.data.items()}
        # NOTE не ясна природа ошибки (только там, где пытаются изменить id ?)
        update_data.pop(self.model._primary_key, None)
        if self.current_entry is None:
            answer = self.model.create(**update_data)
            if identify_error(answer):
                self.parent.returned_entry = None
                showerror(title, collect_message(answer))
            else:
                answer = self.model.select_by_id(answer[self.model._primary_key])
                self.parent.returned_entry = answer
                showinfo(
                    f'{self._SHOWTITLE}: добавление',
                    f'{self._SHOWTITLE} №{self.parent.returned_entry[self.model._primary_key]} успешно добавлен'
                )
                self._quit()
        else:
            answer = self.model.update_by_id(self.current_entry, **update_data)
            if identify_error(answer):
                self.parent.returned_entry = None
                showerror(title, collect_message(answer))
            else:
                answer = self.model.select_by_id(answer[self.model._primary_key])
                self.parent.returned_entry = answer
                showinfo(
                    f'{self._SHOWTITLE}: обновление',
                    f'{self._SHOWTITLE} №{self.parent.returned_entry[self.model._primary_key]} успешно обновлен'
                )
                self._quit()


class TreatyEditWindow(BaseEditWindow):
    """Окно редактирования договоров"""
    _APPTITLE = 'Добавить/редактировать договор'
    _SHOWTITLE = 'Договор'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'IDTreaty': {
            'title': 'Номер договора:',
            'widget': IdEntry,
            'widget_attrs': {
                'entry_width': _BASE_ENTRY_WIDTH,
                '_default_value': 0,
            },
        },
        'CustomerID': {
            'title': 'Арендатор:',
        },
        'DateStart': {
            'title': 'Начало действия:',
            'widget': DateEntry,
            'widget_attrs': {
                'width': 27,
                'date_pattern': 'y-mm-dd',
            },
        },
        'StopDate': {
            'title': 'Окончание действия:',
            'widget': DateEntry,
            'widget_attrs': {
                'width': 27,
                'date_pattern': 'y-mm-dd',
            },
        },
        'SignDate': {
            'title': 'Дата подписания:',
            'widget': DateEntry,
            'widget_attrs': {
                'width': 27,
                'date_pattern': 'y-mm-dd',
            },
        },
        'Advertisement': {
            'title': 'Изготовление рекламы:',
            'widget': CheckbuttonEntry,
            'widget_attrs': {},
        },
        'Cost': {
            'title': 'Стоимость изготовления:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Leasing': {
            'title': 'Стоимость аренды щита:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'EmployeeID': {
            'title': 'Ответственный от агенства:',
        },
        'PeriodID': {
            'title': 'Оплата:',
        },
        'BillboardID': {
            'title': 'Рекламный щит:',
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {
        'BillboardID': 'get_billboards',
        'CustomerID': 'get_customers',
        'EmployeeID': 'get_employees',
        'PeriodID': 'get_periods',
    }

    def get_employees(self):
        """Получить всех ответственных"""
        return {
            row['IDEmployee']: row['Employee']
            for row in self.model._fields['EmployeeID'].select_all()
        }

    def get_customers(self):
        """Получить всех арендаторов"""
        return {
            row['IDCustomer']: row['Customer']
            for row in self.model._fields['CustomerID'].select_all()
        }

    def get_periods(self):
        """Получить все периоды оплаты"""
        return {
            row['IDPeriod']: row['Period']
            for row in self.model._fields['PeriodID'].select_all()
        }

    def get_billboards(self):
        """Получить все номер рекламных щитов"""
        return {
            row['IDBillboard']: row['IDBillboard']
            for row in self.model._fields['BillboardID'].select_all()
        }


class AdminEditWindow(BaseEditWindow):
    """Окно администратора для редактирования пользователей"""
    _APPTITLE = 'Добавить/редактировать пользователя'
    _SHOWTITLE = 'Пользователь'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'Login': {
            'title': 'Логин:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Password': {
            'title': 'Пароль:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
                'show': '*',
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class CustomerEditWindow(BaseEditWindow):
    """Окно для редактирования арендаторов"""
    _APPTITLE = 'Создать/редактировать арендатора'
    _SHOWTITLE = 'Арендатор'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'INN': {
            'title': 'ИНН арендатора:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Status': {
            'title': 'Статус арендатора:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Customer': {
            'title': 'Название:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'AddressCust': {
            'title': 'Юридический адрес:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Bank': {
            'title': 'Банк:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Account': {
            'title': 'Номер счета:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Tax': {
            'title': 'Налоговая инспекция:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Chief': {
            'title': 'Руководитель:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Phone': {
            'title': 'Телефон руководителя:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class EmployeeEditWindow(BaseEditWindow):
    """Окно для редактирования ответственного"""
    _APPTITLE = 'Создать/редактировать ответственного'
    _SHOWTITLE = 'Ответственный от агенства'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'Employee': {
            'title': 'Ответственный от агенства:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class PeriodEditWindow(BaseEditWindow):
    """Окно для редактирования периода оплаты"""
    _APPTITLE = 'Создать/редактировать ответственного'
    _SHOWTITLE = 'Период оплаты'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'Period': {
            'title': 'Пеиод оплаты:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class BillboardEditWindow(BaseEditWindow):
    """Окно для редактирования рекламного щита"""
    _APPTITLE = 'Создать/редактировать рекламный щит'
    _SHOWTITLE = 'Рекламный щит'
    _WITH_PICTURE = True
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'IDBillboard': {
            'title': 'Номер щита:',
            'widget': IdEntry,
            'widget_attrs': {
                'entry_width': _BASE_ENTRY_WIDTH,
                '_default_value': 0,
            },
        },
        # 'TreatyID': {
        #     'title': 'Номер договора аренды:',
        # },
        'Address': {
            'title': 'Адрес расположения:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Orientation': {
            'title': 'Местоположение:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Square': {
            'title': 'Площадь щита:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'District': {
            'title': 'Район города:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Size': {
            'title': 'Размер щита:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Picture': {
            'title': 'Фотография (путь):',
            'widget': FilenameEntry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {
        # 'TreatyID': 'get_treaties',
        # 'CategoryID': 'get_categories',
    }

    # def get_treaties(self):
    #     """Получить все договоры"""
    #     return {row['IDTreaty']: row['IDTreaty'] for row in self.model._fields['TreatyID'].select_all()}

    # def get_categories(self):
    #     """Получить все категории"""
    #     return {row['IDCategory']: row['Category'] for row in self.model._fields['CategoryID'].select_all()}

    def _make_widgets(self):
        """Виджет с картинкой"""
        row = len(self._ROWS_LIST)
        if self.current_object is not None and (img := self.current_object['Picture']):
            self.current_image = ModuleImage(self.main_frame, f'save_images/{img}')
            self.current_image.grid(row=row, column=0, columnspan=2)
        else:
            self.current_image = ModuleImage(self.main_frame)
            self.current_image.grid(row=row, column=0, columnspan=2)

        super()._make_widgets()
