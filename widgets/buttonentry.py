import itertools
import os
import os.path
import shutil
import tkinter as tk
import uuid

from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror, showinfo


class FilenameEntry(tk.Frame):
    """Виджет поля ввода Entry с кнопкой"""
    _frame_specific = ('height', 'highlightbackground', 'highlightthickness',)
    _entry_specific = (
        'command', 'font', 'exportselection', 'fg', 'justify',
        'selectbackground', 'selectborderwidth', 'selectforeground',
        'show', 'state', 'textvariable', 'xscrollcommand',
    )
    # наверное, будут использоваться для Frame
    _common_options = ('bg', 'bd', 'cursor', 'highlightcolor', 'relief', 'width')

    def __init__(self, master=None, cnf={}, **kw):
        # сохранить имя файла
        self.filename = ''
        # выделить команду для кнопки
        # self.button_command = kw.pop('button_command', cnf.pop('button_command', None))
        # self.button_text = kw.pop('text', cnf.pop('text', '!without text'))
        # выделить параметры для Entry
        self._entry_options_cnf, self._entry_options_kw = self._get_options(
            cnf, kw, self._entry_specific
        )
        # выделить параметры для Frame (в том числе общие)
        kw, cnf = self._get_options(
            cnf, kw, itertools.chain(self._frame_specific, self._common_options)
        )
        # ширину width применим также для Entry
        self.entry_width = kw.get('width', cnf.get('width'))
        super().__init__(master, cnf, **kw)
        self._make_widgets()

    def _get_options(self, cnf, kw, iterator):
        """Разделить опции виджетов"""
        # kw.pop('entry_width', cnf.pop('entry_width', 30))
        return (
            {key: value for key, value in cnf.items() if key in list(iterator)},
            {key: value for key, value in kw.items() if key in list(iterator)}
        )

    def _make_widgets(self):
        frame = tk.Frame(self)
        frame.pack(expand=tk.YES, fill=tk.BOTH)

        self.entry = tk.Entry(
            frame,
            width=self.entry_width,
            validate='focusin',
            validatecommand=self.get_filename,
            cnf=self._entry_options_cnf,
            **self._entry_options_kw
        )
        self.entry.pack()

        # tk.Button(
        #     frame,
        #     # text=self.button_text,
        #     # command=lambda e=self.entry: (btc(e) if (btc := self.button_command) is not None else None)
        #     text='Загрузить',
        #     command=self.save_file
        # ).pack(side=tk.RIGHT, pady=5)

    def get(self):
        """Для чтения данных поля ввода"""
        # if not self.filename:
        return self.save_file()
        # else:
            # return self.filename

    def insert(self, index, string):
        self.entry.insert(index, string if string else '')

    def get_filename(self):
        """Получить имя файла"""
        # Это self.main_frame
        # print(self.master)
        filename = askopenfilename(initialdir='.',
            # filetypes=(
            #     'Image files',
            #     ['*.jpg', '*.jpeg']# *.tiff *.gif *.bmp'
            # )
        )
        self.entry.delete(0, tk.END)
        self.entry.insert(0, filename)

    def save_file(self):
        """Сохраняет файл, когда нажимается кнопка 'Загрузить'."""
        filename = self.entry.get()
        self.filename = ''.join((
            str(uuid.uuid1()),
            os.path.splitext(filename)[1]
        ))
        if filename:
            try:
                shutil.copy(filename, 'save_images')
                os.rename(
                    f'save_images/{os.path.basename(filename)}',
                    f'save_images/{self.filename}'
                )
            except Exception as e:
                showerror('Загрузка файла', f'Файл не загружен. Ошибка: {e}')
                self.filename = ''
            else:
                # self.filename = filename
                showinfo('Загрузка файла', 'Файл успешно загружен')
        else:
            showerror('Загрузка файла', 'Не указано имя файла')
            self.filename = ''
        return self.filename


if __name__ == '__main__':
    root = tk.Tk()

    bentry = FilenameEntry(root, width=60)
    bentry.pack(padx=20, pady=20)

    def print_button():
        print(bentry.get())

    tk.Button(root, text='Получить имя файла', command=print_button).pack(pady=10)

    root.mainloop()