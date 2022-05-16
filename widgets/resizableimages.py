import tkinter as tk

from PIL import Image, ImageTk


class ModuleImage(tk.Frame):
    __MAX_HEIGHT = 150
    def __init__(self, master, image=None, maxheight=None, cnf={}, **kwargs):
        super().__init__(master, cnf, **kwargs)
        self.maxheight = maxheight or ModuleImage.__MAX_HEIGHT
        self.image = image and Image.open(image)
        if self.image:
            self._make_image()

    def updateImage(self, image=None):
        if self.image:
            self.background.destroy()
        self.image = image and Image.open(image)
        if self.image:
            self._make_image()

    def clearImage(self):
        # ERROR: если еще не был показан модуль (соответственно нет картинки)
        if hasattr(self, 'background'):
            self.background.destroy()
        # self.update()

    def _make_image(self):
        """Создание картинки."""
        self.img_copy= self.image.copy()

        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = tk.Label(self, image=self.background_image)
        self.background.pack(fill=tk.BOTH, expand=tk.YES)
        self._resize_image()
        # self.background.bind('<Configure>', self._resize_image)

    def _resize_image(self):
        """Событие изменения размера картинки."""
        width, height = self.image.size
        reduction = (height / self.maxheight)
        new_width = round(width / reduction)
        new_height = round(height / reduction)

        self.image = self.img_copy.resize((new_width, new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image=self.background_image)
