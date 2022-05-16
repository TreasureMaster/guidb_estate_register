import os
from windows import StartWindow


try:
    os.mkdir('save_images')
except FileExistsError:
    pass

try:
    os.mkdir('temp_files')
except FileExistsError:
    pass

# Отсюда запускаем код
app = StartWindow()


if __name__ == '__main__':
    app.run()