# -------------------------- Вспомогательные функции ------------------------- #

def identify_error(checked_dict, key_prefix='!error'):
    """Проверка словаря на содержание ошибок (начинающихся с префикса !error)"""
    return any([True for key in checked_dict.keys() if key.startswith(key_prefix)])

def collect_message(messages, title='Список ошибок:', key_prefix='!error'):
    """Собирает строку сообщений (по умолчанию ошибки) из словаря отдельных сообщений"""
    if title:
        title += '\n'
    return title + '\n'.join((
        f'{num}. {value}'
        for num,( key, value) in enumerate(messages.items(), start=1)
        if key.startswith(key_prefix)
    ))

def update_error_keys(messages, key_prefix='!error_'):
    """Изменяет ключи ошибок для идентификации ошибок, полученных из marshmallow"""
    return {
        f'{key_prefix}{num}': f"Ошибка поля '{key}': {'; '.join(value) if isinstance(value, list) else value}"
        for num, (key, value) in enumerate(messages.items(), start=1)
    }


if __name__ == '__main__':
    messages = {}
    print(collect_message(messages))
    messages = {'!error': 'error one'}
    print(collect_message(messages))
    messages = {
        '!error_1': 'error 1',
        '!error_2': 'error 2',
        '!error_3': 'error 3',
    }
    print(collect_message(messages, title='Несколько ошибок'))
    messages = {
        '!error_1': 'error 1',
        '!error_2': 'error 2',
        '!error_3': 'error 3',
        'name': 'valid field',
    }
    print(collect_message(messages, title='Есть поле без ошибок'))
    messages = {
        '!error_1': 'error 1',
        '!error_2': 'error 2',
        '!error_3': 'error 3',
        'name': 'valid field',
    }
    print(collect_message(messages, title='Вывести поле без ошибок', key_prefix=''))
    print('change_keys ' + '-'*30)
    messages = {
        'email': 'error 1',
        'Status': 'error 2',
        'Address': 'error 3',
        'name': 'valid field',
    }
    print(update_error_keys(messages))