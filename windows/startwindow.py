import tkinter as tk
from tkinter.messagebox import showerror

from models import UserModel, PGCursor
from extras import identify_error, collect_message
# from windows import AdminMainWindow, ContractMainWindow

class StartWindow:
    """Стартовое окно приложения."""
    __APPTITLE = 'Авторизация'

    def __init__(self):
        self.user = UserModel(PGCursor())
        self.window = tk.Tk()
        self.window.title(StartWindow.__APPTITLE)
        self._make_widgets()
        # super().__init__()

    def run(self):
        """Теперь только непосредственно старт."""
        self.window.mainloop()
 
    def _make_widgets(self):
        widget_width = 30
        btn_width = 10
        main_frame = tk.Frame(self.window)
        main_frame.pack(expand=tk.YES, fill=tk.BOTH, padx=30, pady=30)
        # main_frame.pack()

        tk.Label(main_frame, text='Логин:', width=btn_width, anchor=tk.W).grid(row=0, column=0)
        tk.Label(main_frame, text='Пароль:', width=btn_width, anchor=tk.W).grid(row=1, column=0)

        self.login = tk.Entry(main_frame, width=widget_width)
        self.login.grid(row=0, column=1, padx=10, pady=10)
        self.password = tk.Entry(main_frame, width=widget_width, show='*')
        self.password.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            main_frame, text='OK',
            command=self.get_user,
            width=btn_width
        ).grid(row=2, column=0, padx=10, pady=10, sticky=tk.E)
        tk.Button(
            main_frame, text='Отмена',
            command=self.window.quit,
            width=btn_width
        ).grid(row=2, column=1, padx=10, pady=10)

    def get_user(self):
        """Получение данных пользователя при входе"""
        from windows import AdminMainWindow, BuildingMainWindow
        who_is = self.user.sign_in(
            self.login.get(),
            self.password.get()
        )
        if identify_error(who_is):
            # showerror('Ошибка авторизации', who_is['!error'])
            showerror('Ошибка авторизации', collect_message(who_is))
        elif who_is['is_admin']:
            print('Переход к окну администратора')
            self.window.withdraw()
            AdminMainWindow(self.window, self.user)
        else:
            print('Переход к окну пользователя')
            self.window.withdraw()
            BuildingMainWindow(self.window)
