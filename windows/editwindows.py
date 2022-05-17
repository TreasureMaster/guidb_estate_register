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
                    # entry.configure(width=10, from_=1, to=100, state='readonly')
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


class BuildingEditWindow(BaseEditWindow):
    """Окно редактирования здания"""
    _APPTITLE = 'Добавить/редактировать здание'
    _SHOWTITLE = 'Здание'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'BuildingName': {
            'title': 'Название корпуса:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Land': {
            'title': 'Площадь:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Address': {
            'title': 'Адрес:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Year': {
            'title': 'Год постройки:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'MaterialID': {
            'title': 'Материал стен:',
        },
        'Wear': {
            'title': 'Износ (%):',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Flow': {
            'title': 'Этажи:',
            'widget': ttk.Spinbox,
            'widget_attrs': {
                'width': 10,
                'from_': 1,
                'to': 100,
                'state': 'readonly'
            },
        },
        'Picture': {
            'title': 'Фото (путь):',
            'widget': FilenameEntry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Comment': {
            'title': 'Доп. информация:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {
        'MaterialID': 'get_materials',
    }

    def get_materials(self):
        """Получить всех материалы"""
        return {
            row['IDMaterial']: row['Material']
            for row in self.model._fields['MaterialID'].select_all()
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


class DepartmentEditWindow(BaseEditWindow):
    """Окно для редактирования кафедр"""
    _APPTITLE = 'Добавить/редактировать кафедру'
    _SHOWTITLE = 'Кафедра'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'DepartmentName': {
            'title': 'Название кафедры:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Boss': {
            'title': 'Заведующий кафедрой:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Phone': {
            'title': 'Телефон кафедры:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'OfficeDean': {
            'title': 'Деканат:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class HallEditWindow(BaseEditWindow):
    """Окно для редактирования помещения"""
    _APPTITLE = 'Создать/редактировать помещение'
    _SHOWTITLE = 'Помещение'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'HallNumber': {
            'title': 'Номер аудитории:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'HallSquare': {
            'title': 'Площадь аудитории:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Windows': {
            'title': 'Окна:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Heaters': {
            'title': 'Батареи:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'TargetID': {
            'title': 'Назначение:',
        },
        'DepartmentID': {
            'title': 'Кафедра:',
        },
        'KadastrID': {
            'title': 'Здание:',
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {
        'TargetID': 'get_targets',
        'DepartmentID': 'get_departments',
        'KadastrID': 'get_buildings',
    }

    def get_targets(self):
        """Получить все назначения помещений"""
        return {
            row['IDTarget']: row['Target']
            for row in self.model._fields['TargetID'].select_all()
        }

    def get_departments(self):
        """Получить все кафедры"""
        return {
            row['IDDepartment']: row['DepartmentName']
            for row in self.model._fields['DepartmentID'].select_all()
        }

    def get_buildings(self):
        """Получить все здания"""
        return {
            row['IDKadastr']: row['BuildingName']
            for row in self.model._fields['KadastrID'].select_all()
        }


class ChiefEditWindow(BaseEditWindow):
    """Окно для редактирования ответственного"""
    _APPTITLE = 'Создать/редактировать ответственного'
    _SHOWTITLE = 'Ответственный за имущество'
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'Chief': {
            'title': 'Фамилия:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'AddressChief': {
            'title': 'Адрес проживания:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Experience': {
            'title': 'Годы опыта:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {}


class UnitEditWindow(BaseEditWindow):
    """Окно для редактирования имущества"""
    _APPTITLE = 'Создать/редактировать имущество'
    _SHOWTITLE = 'Имущество'
    _WITH_PICTURE = True
    _BASE_ENTRY_WIDTH = 30
    _ROWS_LIST = {
        'UnitName': {
            'title': 'Название имущества:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'DateStart': {
            'title': 'Дата постановки:',
            'widget': DateEntry,
            'widget_attrs': {
                'width': 27,
                'date_pattern': 'y-mm-dd',
            },
        },
        'Cost': {
            'title': 'Стоимость:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'CostYear': {
            'title': 'Год переоценки:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'CostAfter': {
            'title': 'Стоимость списания:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'Period': {
            'title': 'Срок службы:',
            'widget': tk.Entry,
            'widget_attrs': {
                'width': _BASE_ENTRY_WIDTH,
            },
        },
        'HallID': {
            'title': 'Установлен в помещении:',
        },
        'ChiefID': {
            'title': 'Ответственный:',
        },
        '!buttons_frame': None
    }
    _COMBO_LIST = {
        'HallID': 'get_halls',
        'ChiefID': 'get_chiefs',
    }

    def get_halls(self):
        """Получить все помещения"""
        return {row['IDHall']: row['HallName'] for row in self.model._fields['HallID'].select_all()}

    def get_chiefs(self):
        """Получить всех ответственных"""
        return {row['IDChief']: row['Chief'] for row in self.model._fields['ChiefID'].select_all()}
