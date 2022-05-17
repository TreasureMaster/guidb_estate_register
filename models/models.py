import hashlib
from psycopg2 import sql
import marshmallow as mm
import marshmallow.validate as mmv

from extras.extra_funcs import collect_message

from .db import PGCursor
from extras import identify_error, update_error_keys


class RequiredField:
    """Просто метка требуемого для ввода поля"""

class backref:
    """Обратная ссылка на другую таблицу"""
    def __init__(self, model_cls):
        self.reference = model_cls

    def __call__(self, pg):
        """Возможно нам нужен только индекс ???"""
        if isinstance(pg, PGCursor):
            self.reference = self.reference(pg)
        else:
            return self

    def check_id(self, index):
        """Проверить есть ли такой id"""
        return self.reference.select_by_id(index)

    def select_all(self):
        """Весь список (для вывода списков в таблицах)"""
        return self.reference.select_all()

    def get_join(self):
        """Добавить обратную ссылку как JOIN"""
        # Надо: JOIN {self.reference._table} ON {self.reference._table}.{self.reference._primary_key}
        # Объединять со своим Primay Key будет внешний родительский объект
        return sql.Composed([
            sql.SQL(' JOIN '),
            sql.Identifier(self.reference._table),
            sql.SQL(' ON '),
            sql.Identifier(self.reference._table, self.reference._primary_key),
            sql.SQL('=')
        ])

    def get_composed(self):
        """Получение SQL-скрипта для составных полей переданной модели из backref"""
        return sql.SQL('').join([
            cp.get_composed()
            for cp in self.reference._fields.values()
            if isinstance(cp, ComposedProperty)
        ])


class ComposedProperty:
    """Составные свойства"""
    def __init__(self, table, composed_property={'title': '', 'fields': (), 'sep': ' '}):
        # Вид composed_property = {
            # title = 'название поля',
            # fields = (кортеж имен, которые будут складываться в одно поле),
            # sep = 'разделитель, с помощью которого имена будут объединяться'
        # }
        self._table = table
        # По умолчанию разделитель полей - это пробел
        if 'sep' not in composed_property:
            composed_property['sep'] = ' '
        self.composed_property = composed_property

    def get_composed(self):
        """Получение одного SQL-скрипта для составного поля"""
        if self.composed_property['fields']:
            return sql.Composed([
                sql.SQL(', CONCAT_WS({},').format(sql.Literal(self.composed_property['sep'])),
                sql.SQL(', ').join(map(lambda s: sql.Identifier(self._table, s), self.composed_property['fields'])),
                sql.SQL(') AS {} ').format(sql.Identifier(self.composed_property['title']))
            ])
            # print('in composed:', a.as_string(self.reference._connection.connection))
        else:
            return sql.SQL(' ')


class BaseModel:

    def __init__(self, connection):
        self._connection = connection
        # Инициализировать модели в обратных ссылках
        for field, entity in self._fields.items():
            if isinstance(entity, backref) and isinstance(entity.reference, type):
                entity(self._connection)

    def encrypt(self, password):
        """Шифрование, н-р, пароля"""
        return hashlib.sha1(password.encode()).hexdigest()

    def execute(self, stmt, vars=None, is_returned=True):
        """Провайдер выполнения запроса"""
        row = None
        with self._connection as pg:
            pg.execute(stmt, vars)
            if is_returned:
                row = pg.fetchone()
        return row

    def execute_get_one(self, stmt, vars=None):
        """Провайдер выполнения запроса с возвратом одной строки"""
        with self._connection as pg:
            pg.execute(stmt, vars)
            row = pg.fetchone()
        return row

    def execute_get_all(self, stmt, vars=None):
        """Провайдер выполнения запроса с возвратом всех найденных строк"""
        with self._connection as pg:
            pg.execute(stmt, vars)
            rows = pg.fetchall()
        return rows

    def clean_fields(self, kwargs):
        """Очистить kwargs от данных, которых нет в списке полей, и от ComposedProperty (это не нужно писать в БД)"""
        return {
            key: value
            for key, value in kwargs.items()
            if key in self._fields.keys() and not isinstance(self._fields[key], ComposedProperty)
        }

    def get_required(self):
        """Возвращает названия колонок, которые не устанавливаются по умолчанию (требующиеся всегда)"""
        return {
            key
            for key, value in self._fields.items()
            if isinstance(value, RequiredField)
        }

    def for_create(self, kwargs):
        """Подготовка инициализации полей"""
        kwargs = self.clean_fields(kwargs)
        # Добавить поля, заданные по умолчанию, если они не переданы
        for key, value in self._fields.items():
            if not isinstance(value, (RequiredField, ComposedProperty, backref)):
                # установка значений по умолчанию
                if (
                    key not in kwargs or\
                    (not value and not isinstance(kwargs[key], type(value)))
                ):
                    kwargs[key] = value
        missing_fields = self.get_required() - set(kwargs.keys())
        if missing_fields:
            return {
                '!error': 'Отсуствуют обязательные поля: {}'.format(
                    ', '.join(missing_fields)
                )
            }
        # Только проверка существования id из другой таблицы
        for key, entity in self._fields.items():
            if isinstance(entity, backref):
                # проверить, есть ли backref с таким id
                row = entity.check_id(kwargs[key])
                if not row:
                    return {
                        '!error': f'Отсуствуют связанное поле "{key}" с индексом {kwargs[key]}'
                    }
        return kwargs

    def for_update(self, kwargs):
        """Подготовка обновления полей БД"""
        # Только выкинуть отсутствующие поля и зашифровать пароль
        if not kwargs:
            return {
                '!error': 'При обновлении должно быть передано хотя бы одно поле'
            }
        kwargs = self.clean_fields(kwargs)
        # установить поля по умолчанию согласно модели конкретной таблицы
        for key, value in kwargs.items():
            if not isinstance(
                self._fields[key],
                (RequiredField, backref, ComposedProperty)
            ):
                if not value and not isinstance(
                    self._fields[key],
                    type(value)
                ):
                    kwargs[key] = self._fields[key]
        # Только проверка существования id из другой таблицы
        for key, entity in self._fields.items():
            if isinstance(entity, backref):
                # проверить, есть ли backref с таким id
                row = entity.check_id(kwargs[key])
                if not row:
                    return {
                        '!error': f'Отсуствуют связанное поле "{key}" с индексом {kwargs[key]}'
                    }
        return kwargs

    def select_by_id(self, index):
        """Получение записи по id"""
        stmt = sql.SQL('SELECT *{}{}FROM {}{} WHERE {}={}').format(
            self.get_backref_composed(),
            self.get_composed_properties(),
            sql.Identifier(self._table),
            self.get_all_join(),
            sql.Identifier(self._primary_key),
            sql.Literal(index)
        )
        # print(stmt.as_string(self._connection.connection))
        return self.execute_get_one(stmt)


    def select_by_field(self, column, value):
        """Выбор из колонки по ее содержимому"""
        stmt = sql.SQL('SELECT *{}{}FROM {}{} WHERE {}={}').format(
            self.get_backref_composed(),
            self.get_composed_properties(),
            sql.Identifier(self._table),
            self.get_all_join(),
            sql.Identifier(column),
            sql.Literal(value)
        )
        return self.execute_get_all(stmt)

    def delete(self, index):
        """Удаление записи по id"""
        if not self.select_by_id(index):
            return {
                '!error': f'{self._entity_name} с номером {index} не существует'
            }
        stmt = sql.SQL('DELETE FROM {} WHERE {}={}').format(
            sql.Identifier(self._table),
            sql.Identifier(self._primary_key),
            sql.Literal(index)
        )
        self.execute(stmt, is_returned=False)

    def clean_input_fields(self, input_fields):
        """Очистить входные поля"""
        return {
            key: value
            for key, value in input_fields.items()
            if 
            (
                (isinstance(self._fields[key], RequiredField) and value != '') or\
                (not isinstance(self._fields[key], RequiredField))
            )
        }

    def create(self, **input_fields):
        """Добавление новой записи"""
        # подготовка данных
        input_fields = self.clean_input_fields(input_fields)
        input_fields = self.for_create(input_fields)
        if identify_error(input_fields):
            return input_fields
        if errors := self.validate(input_fields):
            return errors
        if 'Password' in input_fields:
            input_fields['Password'] = self.encrypt(input_fields['Password'])
        stmt = sql.SQL('INSERT INTO {} ({}) VALUES ({}) RETURNING *').format(
            sql.Identifier(self._table),
            sql.SQL(', ').join(map(sql.Identifier, input_fields.keys())),
            sql.SQL(', ').join(map(sql.Placeholder, input_fields.keys()))
        )
        # print(stmt.as_string(pg))
        # print(input_fields)
        return self.execute(stmt, input_fields)

    def update_by_id(self, index, **input_fields):
        """Обновление данных существующей записи"""
        if not self.select_by_id(index):
            return {
                '!error': f'{self._entity_name} с номером {index} не существует'
            }
        input_fields = self.clean_input_fields(input_fields)
        input_fields = self.for_update(input_fields)
        if identify_error(input_fields):
            return input_fields
        if errors := self.validate(input_fields, partial=True):
            return errors
        if 'Password' in input_fields:
            input_fields['Password'] = self.encrypt(input_fields['Password'])
        stmt = sql.SQL('UPDATE {} SET {} WHERE {}={} RETURNING *').format(
            sql.Identifier(self._table),
            sql.SQL(', ').join(
                map(
                    lambda key: sql.SQL('=').join(
                        (sql.Identifier(key), sql.Placeholder(key))
                    ),
                    input_fields
                )
            ),
            sql.Identifier(self._primary_key),
            sql.Literal(index)
        )
        # print(stmt.as_string(pg))
        return self.execute(stmt, input_fields)

# ---------------------------- Эти можно оставить ---------------------------- #
    def select_like(self, field, key, order_by=None):
        """Поиск по совпадению поля с частью содержимого поля
        
        :param field: Колонка таблицы, в которой нужно искать значение
        :param key:   Ключ, по которому производится поиск
        :param order_by: Поле, по которому сортируется
        """
        stmt = sql.SQL('SELECT *{}{}FROM {}{} WHERE {} {} ORDER BY {}').format(
            self.get_backref_composed(),
            self.get_composed_properties(),
            sql.Identifier(self._table),
            self.get_all_join(),
            sql.Identifier(*field.split('.')),
            self.get_and_stmt(key),
            sql.Identifier(self._primary_key if order_by is None else order_by)
        )
        # print(stmt.as_string(self._connection.connection))
        return self.execute_get_all(stmt)

    def get_and_stmt(self, key):
        """Объединение поиска для нескольких условий через AND"""
        return (
                sql.Composed([sql.SQL('= '), sql.Literal(key)])
                if key.isdigit() else
                sql.Composed([sql.SQL('LIKE '), sql.Literal(f'%{key}%')])
            )

    def select_likes(self, fields, order_by=None):
        """Поиск по совпадению нескольких полей с частью содержимого этих полей
        
        :param fields: Словарь, где ключ - поле, где искать, а значение - ключ поиска это поля
        :param order_by: Поле, по которому сортируется
        """
        stmt = sql.SQL('SELECT *{}{}FROM {}{} WHERE {} ORDER BY {}').format(
            self.get_backref_composed(),
            self.get_composed_properties(),
            sql.Identifier(self._table),
            self.get_all_join(),
            sql.SQL(' AND ').join(
                map(
                    lambda item: sql.SQL(' ').join(
                        (sql.Identifier(*item[0].split('.')), self.get_and_stmt(item[1]))
                    ),
                    fields.items()
                )
            ),
            sql.Identifier(self._primary_key if order_by is None else order_by)
        )
        # print(stmt.as_string(self._connection.connection))
        return self.execute_get_all(stmt)

    def get_all_join(self):
        """Скомпоновать все JOIN"""
        return sql.SQL(' ').join(map(
            lambda f: sql.Composed([f[1], sql.Identifier(self._table, f[0])]),
            (
                (field, entity.get_join())
                for field, entity in self._fields.items()
                if isinstance(entity, backref)
            )
        ))
        # print('---> join:', f'"{a.as_string(self._connection.connection)}"')

    def get_backref_composed(self):
        """Получить запрос для составных элементов backref"""
        return sql.SQL('').join(
            entity.get_composed()
            for _, entity in self._fields.items()
            if isinstance(entity, backref)
        )

    def get_composed_properties(self):
        """Получить запрос для всех составных элементов текущей таблицы"""
        query = sql.SQL('').join(
            entity.get_composed()
            for _, entity in self._fields.items()
            if isinstance(entity, ComposedProperty)
        )
        return query if query else sql.SQL(' ')

    def select_all(self):
        """Выбрать всю таблицу"""
        stmt = sql.SQL('SELECT *{}{}FROM {}{} ORDER BY {}').format(
            self.get_backref_composed(),
            self.get_composed_properties(),
            sql.Identifier(self._table),
            self.get_all_join(),
            sql.Identifier(self._primary_key),
        )
        # print(stmt.as_string(self._connection.connection))
        return self.execute_get_all(stmt)

    def validate(self, input_fields, partial=None):
        """Проверка полей ввода с помощью marshmallow"""
        errors = self.__class__.ValidateSchema().validate(input_fields, partial=partial)
        if errors:
            return update_error_keys(errors)


# ----------------------- Конкретные модели приложения ----------------------- #


class UserModel(BaseModel):
    """Модель пользователя"""
    _table = 'users'
    _entity_name = 'Пользователь'
    _primary_key = 'IDUser'
    _fields = {
        'Login': RequiredField(),
        'Password': RequiredField(),
        'is_admin': False
    }
    class ValidateSchema(mm.Schema):
        """Схема валидации модели."""
        Login = mm.fields.String(required=True)
        Password = mm.fields.String(required=True)
        is_admin = mm.fields.Boolean(required=True)

    def sign_in(self, login, password):
        """Вход в программу"""
        stmt = sql.SQL('SELECT * FROM {} WHERE {}={}').format(
            sql.Identifier(self._table),
            sql.Identifier('Login'),
            sql.Literal(login)
        )
        row = self.execute_get_one(stmt)
        if not row:
            return {'!error': f'Пользователя с логином "{login}" не существует'}
        if row['Password'] != self.encrypt(password):
            return {'!error': f'Введенный пароль не совпадает'}

        return {'is_admin': row['is_admin']}

    def create(self, **input_fields):
        """Добавление нового пользователя"""
        # проверка вставки дубликата уникальных имен
        if self.select_by_field('Login', input_fields['Login']):
            return {'!error': f'''Пользователь с логином "{input_fields['Login']}" уже существует'''}
        return super().create(**input_fields)


class MaterialModel(BaseModel):
    """Модель материала здания"""
    _table = 'materials'
    _entity_name = 'Материал'
    _primary_key = 'IDMaterial'
    _fields = {
        'Material': RequiredField(),
    }


class TargetModel(BaseModel):
    """Модель назначения помещения"""
    _table = 'targets'
    _entity_name = 'Тип помещения'
    _primary_key = 'IDTarget'
    _fields = {
        'Target': RequiredField(),
    }


class DepartmentModel(BaseModel):
    """Модель кафедры"""
    _table = 'departments'
    _entity_name = 'Кафедра'
    _primary_key = 'IDDepartment'
    _fields = {
        'DepartmentName': RequiredField(),
        'Boss': RequiredField(),
        'Phone': RequiredField(),
        'OfficeDean': RequiredField(),
    }


class BuildingModel(BaseModel):
    """Модель здания"""
    _table = 'buildings'
    _entity_name = 'Здание'
    _primary_key = 'IDKadastr'
    _fields = {
        'BuildingName': RequiredField(),
        'Land': RequiredField(),
        'Address': RequiredField(),
        'Year': RequiredField(),
        'Wear': RequiredField(),
        'Flow': RequiredField(),
        'Picture': None,
        'Comment': None,
        'MaterialID': backref(MaterialModel),
    }


class HallModel(BaseModel):
    """Модель помещения"""
    _table = 'halls'
    _entity_name = 'Помещение'
    _primary_key = 'IDHall'
    _fields = {
        'HallNumber': RequiredField(),
        'HallSquare': RequiredField(),
        'Windows': RequiredField(),
        'Heaters': RequiredField(),
        'DepartmentID': backref(DepartmentModel),
        'KadastrID': backref(BuildingModel),
    }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     INN = mm.fields.Integer(required=True)
    #     Status = mm.fields.String(required=True)
    #     Customer = mm.fields.String(required=True)
    #     AddressCust = mm.fields.String(required=True)
    #     Bank = mm.fields.String(required=True)
    #     # Account = mm.fields.String(required=True, validate=mmv.Length(equal=20))
    #     Account = mm.fields.String(required=True)
    #     Tax = mm.fields.String(required=True)
    #     Chief = mm.fields.String(required=True)
    #     Phone = mm.fields.String(required=True)

    #     @mm.validates('Account')
    #     def validate_account(self, value):
    #         if not value.isdigit():
    #             raise mm.ValidationError('принимаются только цифры')
    #         elif len(value) != 20:
    #             raise mm.ValidationError('длина должна быть точно 20 символов')

    #     @mm.validates('INN')
    #     def validate_inn(self, value):
    #         if not (9 < len(str(value)) < 13):
    #             raise mm.ValidationError('длина ИНН 10 или 12 цифр')

    #     @mm.validates('Phone')
    #     def validate_phone(self, value):
    #         if set(value) - set('0123456789-()+ '):
    #             raise mm.ValidationError('недопустимый символ')

class ChiefModel(BaseModel):
    """Модель ответственного"""
    _table = 'chiefs'
    _entity_name = 'Ответственный'
    _primary_key = 'IDChief'
    _fields = {
        'Chief': RequiredField(),
        'AddressChief': RequiredField(),
        'Experience': RequiredField(),
    }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     Address = mm.fields.String(required=True)
    #     Orientation = mm.fields.String(required=True)
    #     Square = mm.fields.Float(required=True)
    #     District = mm.fields.String(required=True)
    #     Size = mm.fields.String(required=True)
    #     Picture = mm.fields.String(allow_none=True)


class UnitModel(BaseModel):
    """Модель имущества"""
    _table = 'units'
    _entity_name = 'Имущество'
    _primary_key = 'IDUnit'
    _fields = {
        'UnitName': RequiredField(),
        'DateStart': RequiredField(),
        'Cost': RequiredField(),
        'CostYear': RequiredField(),
        'CostAfter': RequiredField(),
        'Period': RequiredField(),
        'HallID': backref(HallModel),
        'ChiefID': backref(ChiefModel),
    }
    # class ValidateSchema(mm.Schema):
    #     """Схема валидации модели."""
    #     DateStart = mm.fields.Date(required=True)
    #     StopDate = mm.fields.Date(required=True)
    #     SignDate = mm.fields.Date(required=True)
    #     Advertisement = mm.fields.Boolean(required=True)
    #     Cost = mm.fields.Float(required=True)
    #     Leasing = mm.fields.Float(required=True)
    #     PeriodID = mm.fields.Integer(required=True)
    #     EmployeeID = mm.fields.Integer(required=True)
    #     BillboardID = mm.fields.Integer(required=True)
    #     CustomerID = mm.fields.Integer(required=True)


if __name__ == '__main__':

    testing = 'client'

    from db import PGCursor

    # pg_cursor = PGCursor(get_db())
    if testing == 'user':
        user = UserModel(PGCursor())

        print('--- sign in check ' + '-'*40)
        answer = user.sign_in('user2', 'pswd')
        print(answer)
        answer = user.sign_in('fake_user', 'pswd')
        print(answer)
        answer = user.sign_in('user2', 'pswd_fake')
        print(answer)

        print('--- create user ' + '-'*40)
        answer = user.create(Login='user_empty_pswd', Password='')
        print(answer)
        answer = user.create(Login='user7', Password='pswd')
        print(answer)
        answer = user.create(Login='user7', Password='pswd')
        print(answer)
        answer = user.create(Login='admin1', Password='pswd', is_admin=True)
        print(answer)
        print('--- delete user ' + '-'*40)
        answer = user.delete(1146)
        print(answer)
        print('--- update user ' + '-'*40)
        answer = user.update_by_id(1, Login='user_update2')
        print(answer)

    # if testing == 'route':
    #     print('--- create route ' + '-'*40)
    #     route = RouteModel(PGCursor())
    #     answer = route.create(
    #         RouteName='Второй',
    #         Country='Россия',
    #         Period=5,
    #         DateDeparture='2021-12-30',
    #         Comment='Экскурсионная программа 2',
    #         WorkerID=1
    #     )
    #     answer = route.update_by_id(3, WorkerID=2)
    #     print(answer)
    #     print(route.select_all())

        # user = UserModel(PGCursor())
        # print(user.select_all())

    # if testing == 'point':
    #     print('--- create point ' + '-'*40)
    #     point = PointModel(PGCursor())
    #     # answer = point.create(
    #     #     Count=1,
    #     #     StartDate='2021-12-12',
    #     #     StopDate='2021-12-13',
    #     #     Hotel='Плаза Мск',
    #     #     TypeHotel='***',
    #     #     RouteID=3
    #     # )
    #     # answer = route.update_by_id(3, WorkerID=2)
    #     # print(answer)
    #     print(point.select_all())

    # if testing == 'contract':
    #     print('--- create contract ' + '-'*40)
    #     contract = ContractModel(PGCursor())
    #     # answer = contract.create(
    #     #     CountPeople=5,
    #     #     Cost=10456.00,
    #     #     Exempt=400,
    #     #     Return=5500,
    #     #     ClientID=3,
    #     #     RouteID=4
    #     # )
    #     # answer = route.update_by_id(3, WorkerID=2)
    #     # print(answer)
    #     # print(ans := contract.select_all())
    #     # print(ans[0])
    #     # print(exempt := ans[0]['Exempt'])
    #     # print(float(exempt))
    #     # contract.select_all()
    #     answer = contract.select_likes({
    #         'client.Lastname': 'кра',
    #         'contract.Cost': 123
    #     })
    #     print('Длина ответа:', len(answer))
    #     print(answer)

    # if testing == 'client':
    #     print('--- select client ' + '-'*40)
    #     client = PledgerModel(PGCursor())

    #     answer = client.select_by_id(1)
    #     # print('Длина ответа:', len(answer))
    #     print(answer)