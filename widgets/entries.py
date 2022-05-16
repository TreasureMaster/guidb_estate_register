import string
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.messagebox import showwarning

import tkcalendar as tkc


class ToggledEntry(tk.Frame):
    """Виджет поля ввода с переключаемой видимостью
    
    :param text: Метка переключателя видимости поля ввода
    :param entry_width: Ширина поля ввода
    """
    def __init__(self, master=None, cnf={}, **kw):
        # TODO реализовать configure
        self.text_label = kw.pop('text', cnf.pop('text', '!without label'))
        self.entry_width = kw.pop('entry_width', cnf.pop('entry_width', 30))
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _make_widgets(self):
        self.is_visibled = tk.BooleanVar()
        check_button = ttk.Checkbutton(
            self,
            text=self.text_label,
            variable=self.is_visibled,
            command=self._change_visible,
        )
        check_button.pack(fill=tk.X)
        self.inner_entry = tk.Entry(self, width=self.entry_width, state=tk.DISABLED)
        self.inner_entry.pack(anchor=tk.W)

    def _change_visible(self):
        """Изменение видимости поля ввода"""
        self.inner_entry.configure(
            state=(tk.NORMAL if self.is_visibled.get() is True else tk.DISABLED)
        )

    def get(self):
        """Получение данных из поля ввода"""
        if self.is_visibled.get():
            return self.inner_entry.get()
        else:
            return ''


class LabeledEntry(tk.Frame):
    """Виджет поля ввода с подписью
    
    :param text: Метка переключателя видимости поля ввода
    :param entry_width: Ширина поля ввода
    """
    def __init__(self, master=None, cnf={}, **kw):
        # TODO реализовать configure
        self.text_label = kw.pop('text', cnf.pop('text', '!without label'))
        self.entry_width = kw.pop('entry_width', cnf.pop('entry_width', 30))
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _make_widgets(self):
        entry_label = tk.Label(
            self,
            text=self.text_label,
            anchor=tk.W
        )
        entry_label.pack(fill=tk.X)
        self.inner_entry = tk.Entry(self, width=self.entry_width)
        self.inner_entry.pack(anchor=tk.W)

    def get(self):
        """Получение данных из поля ввода"""
        return self.inner_entry.get()


class BaseCustomEntry(tk.Frame):
    """Абстрактный класс для всех виджетов поля ввода"""

    def __init__(self, master=None, cnf={}, **kw):
        # Значение по умолчанию для внутренней переменной; если не задано, то None
        self._default_value = kw.pop('_default_value', cnf.pop('_default_value', None))
        self.entry_width = kw.pop('entry_width', cnf.pop('entry_width', 30))
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _make_widgets(self):
        """Создание виджетов внутри фрейма"""
        self._set_inner_value()

    def _set_inner_value(self, var_type='string'):
        """Установить тип внутренней переменной"""
        self._inner_value = {
            'string': tk.StringVar,
            'int': tk.IntVar,
            'float': tk.DoubleVar,
            'bool': tk.BooleanVar,
        }[var_type](value=self._default_value)

    def get(self):
        """Получить данные из виджета."""
        return self._inner_value.get()

    def set(self, value):
        """Установить данные в виджете"""
        self._inner_value.set(value)


class NullableDateEntry(BaseCustomEntry):
    """Виджет поля ввода даты с возможностью ввода значения NULL"""

    def _make_widgets(self):
        # self._set_inner_value(var_type='bool', value=True)
        self._set_inner_value('bool')

        self.inner_entry = tkc.DateEntry(self, date_pattern='y-mm-dd')#, width=self.entry_width)
        self.inner_entry.pack(side=tk.LEFT)

        tk.Checkbutton(self, text='Установить дату ?', variable=self._inner_value).pack(side=tk.LEFT, padx=10)

    def get(self):
        """Получение данных из поля ввода"""
        if self._inner_value.get():
            return self.inner_entry.get_date()

    def set(self, value):
        """Установка значения поля ввода"""
        return self.inner_entry.set_date(value)


class IdEntry(BaseCustomEntry):
    """Виджет поля ввода только с отображением индекса БД id"""

    def _make_widgets(self):
        self._set_inner_value('int')

        self.inner_entry = tk.Entry(
            self, state='readonly',
            textvariable=self._inner_value,
            width=self.entry_width,
        )
        self.inner_entry.pack(side=tk.LEFT)
        self.inner_entry.bind('<Button-1>', self.input_warn)

    def input_warn(self, event):
        """Событие нажатия на поле ввода"""
        if int(self.get()):
            showwarning('Поле ввода', 'Вы не можете изменить номер.\nСоздайте новую запись.')
        else:
            showwarning('Поле ввода', 'При создании новой записи номер будет присвоен автоматически.')


class CheckbuttonEntry(BaseCustomEntry):
    """Обертка виджета Checkbutton для соответствия общему интерфейсу"""

    def _make_widgets(self):
        self._set_inner_value('bool')

        self.inner_entry = tk.Checkbutton(self, variable=self._inner_value)
        self.inner_entry.pack(side=tk.LEFT)


# class PositiveIntEntry(BaseCustomEntry):
#     """Поле ввода с ограничениями (данный вариант для положительных чисел)"""
#     def __init__(self, master=None, cnf={}, **kw):
#         # Максимально допустимое значение для внутренней переменной; если не задано, то None (не контролируется)
#         self._max_value = kw.pop('_max_value', cnf.pop('_max_value', None))
#         # Минимально допустимое значение для внутренней переменной; если не задано, то None (не контролируется)
#         self._min_value = kw.pop('_min_value', cnf.pop('_min_value', None))
#         # Тип данных; если не задано None (не проверяется)
#         # self._value_type = kw.pop('_value_type', cnf.pop('_value_type', None))
#         super().__init__(master, cnf, **kw)

#     def _make_widgets(self):
#         # self._set_inner_value(self._value_type)
#         self._set_inner_value('int')

#         self.inner_entry = tk.Entry(self, textvariable=self._inner_value)
#         self.inner_entry.pack(side=tk.LEFT)
#         self.inner_entry.bind('<Key>', self.input_warn)

#     def input_warn(self, event):
#         """Событие нажатия на поле ввода"""
#         try:
#             a = int(self._inner_value.get())
#             print(a)
#         except Exception:
#             showwarning('Поле ввода', 'Введен недопустимый символ.')

        # if int(self.get()):
        #     showwarning('Поле ввода', 'Вы не можете изменить номер.\nСоздайте новую запись.')
        # else:
        #     showwarning('Поле ввода', 'При создании новой записи номер будет присвоен автоматически.')


if __name__ == '__main__':
    root = tk.Tk()
    # frame = ToggledEntry(root)
    frame = ToggledEntry(root, text='По фамилии:', entry_width=20)
    frame.pack(fill=tk.X, padx=10, pady=10)

    frame2 = LabeledEntry(root, text='По списку:')
    frame2.pack(fill=tk.X, padx=10, pady=10)

    frame3 = NullableDateEntry(root, _default_value=True)
    frame3.pack(fill=tk.X, padx=10, pady=10)

    frame4 = IdEntry(root, _default_value=0)
    frame4.pack(fill=tk.X, padx=10, pady=10)

    frame5 = CheckbuttonEntry(root)
    frame5.pack(fill=tk.X, padx=10, pady=10)

    # frame6 = PositiveIntEntry(root)
    # frame6.pack(fill=tk.X, padx=10, pady=10)

    def check():
        print(f'"{frame.get()}"')

    def check3():
        print(f'{frame3.get()}')

    def check4():
        print(f'{frame4.get()}')

    def check_value(widget):
        print(f'{widget.get()}')

    btn = tk.Button(root, text='Get', command=check)
    btn.pack(side=tk.LEFT, padx=10)

    btn2 = tk.Button(root, text='Get 3', command=check3)
    btn2.pack(side=tk.LEFT)

    btn3 = tk.Button(root, text='Set ID=4', command=lambda: frame4.set(4))
    btn3.pack(side=tk.LEFT)

    btn4 = tk.Button(root, text='Get 4', command=lambda: check_value(frame4))
    btn4.pack(side=tk.LEFT)

    btn5 = tk.Button(root, text='Get 5', command=lambda: check_value(frame5))
    btn5.pack(side=tk.LEFT)

    # btn6 = tk.Button(root, text='Get 6', command=lambda: check_value(frame6))
    # btn6.pack(side=tk.LEFT)

    print('is DateEntry:', isinstance(frame3, tkc.DateEntry))

    root.mainloop()
    # methods = dir(tkc.DateEntry)
    # for method in dir(tk.Frame):
    #     if method in methods:
    #         print(method)