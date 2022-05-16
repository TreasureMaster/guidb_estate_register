import os
import shutil
import tkinter as tk
import uuid

from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo


class BaseBox(tk.Frame):
    """Базовый фрейм панели Box."""

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self._init()
        self._make_widgets()

    def _init(self):
        """Запуск внутренних настроек"""
        self._create_inner_value()
        self._convert_inner_value()

    def _create_inner_value(self):
        """Задание внутренней переменной
        (необходимо переопределять в дочерних классах)"""
        self._inner_value = None

    def _convert_inner_value(self):
        """Задание метода конвертирования во внутреннее значение
        (можно переопределять в дочерних классах)"""
        # По умолчанию не конвертирует, возвращает сам себя
        self._value_convert = lambda obj: obj

    def _make_widgets(self):
        """Построение виджетов, реализуемое в дочерних классах"""
        raise NotImplementedError

    # NOTE реализация унифицированных методов доступа (get и set) к значению кастомного виджета
    def set(self, value):
        if self._inner_value is None:
            raise AttributeError('Внутренняя переменная не задана.')
        self._inner_value.set(
            self._value_convert(value)
        )

    def get(self):
        if self._inner_value is None:
            raise AttributeError('Внутренняя переменная не задана.')
        return self._inner_value.get()


class RadioBox(BaseBox):
    """Панель из 2 кнопок RadioButton"""

    def _create_inner_value(self):
        self._inner_value = tk.BooleanVar()

    def _convert_inner_value(self):
        self._value_convert = bool

    def _make_widgets(self):
        tk.Radiobutton(
            self, variable=self._inner_value, value=True, text='Да'
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            self, variable=self._inner_value, value=False, text='Нет'
        ).pack(side=tk.LEFT)


class ButtonsBox(BaseBox):
    """Панель с кнопками загрузкт/отмены"""

    def _create_inner_value(self):
        self._inner_value = tk.StringVar()

    def _convert_inner_value(self):
        self._value_convert = str

    def _make_widgets(self):
        tk.Button(
            self, text='Загрузить', command=self.load_filename
        ).pack(side=tk.LEFT, padx=10)
        tk.Button(
            self, text='Отменить', command=self.clear_filename
        ).pack(side=tk.LEFT, padx=10)

    def load_filename(self):
        """Загрузка имени файла"""
        filename = askopenfilename(initialdir='.')
        if filename:
            new_filename = ''.join((
                str(uuid.uuid1()),
                os.path.splitext(filename)[1]
            ))
            try:
                shutil.copy(filename, 'save_images')
                os.rename(
                    f'save_images/{os.path.basename(filename)}',
                    f'save_images/{new_filename}'
                )
            except Exception as e:
                showerror('Загрузка файла', f'Файл не загружен. Ошибка: {e}')
                filename = ''
            else:
                filename = new_filename
                showinfo('Загрузка файла', 'Файл успешно загружен')
        # else:
        #     showerror('Загрузка файла', 'Не указано имя файла')
        #     self.filename = ''
        self._inner_value.set(filename)

    def clear_filename(self):
        """Очистка значения внутренней переменной (имени файла)"""
        self._inner_value.set('')


if __name__ == '__main__':
    root = tk.Tk()
    # testing = 'radiobox'
    testing = '2buttons'

    if testing == 'radiobox':
        widget = RadioBox(root)
    elif testing == '2buttons':
        widget = ButtonsBox(root)

    widget.pack(padx=20, pady=20)

    widget.set(None)
    print(widget.get())

    def get_value():
        print(widget.get())

    btn = tk.Button(root, text='Get value', command=get_value)
    btn.pack()

    root.mainloop()