import click
import psycopg2
import psycopg2.extras

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .config import PG_DB_NAME, SQL_INIT_FILE


def get_db(dbname='postgres'):
    connection = psycopg2.connect(
            dbname=dbname,
            user='postgres',
            password='root',
            host='127.0.0.1',
            port='5432'
        )
    return connection

def connect_db(dbname=PG_DB_NAME):
    """Присоединиться к конкретной БД (из config.py)"""
    return get_db(dbname)

def db_exists(db_name):
    """Проверка существования БД"""
    with get_db().cursor() as cursor:
        cursor.execute("""SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{}'""".format(db_name))
        exists = cursor.fetchone()
    return exists is not None

def db_create(db_name):
    """Создание БД"""
    conn = get_db()
    if not db_exists(db_name):
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("""CREATE DATABASE {}""".format(db_name))

def db_delete(db_name):
    """Удаление БД"""
    conn = get_db()
    if db_exists(db_name):
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cursor:
            cursor.execute("""DROP DATABASE {}""".format(db_name))

def db_fill(sql_file, db_name):
    """Заполнить БД из скрипта SQL"""
    conn = get_db(db_name)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cursor:
        cursor.execute(open(sql_file, 'r', encoding='utf-8').read())

@click.command('init-db')
@click.option('--sql-file', '-f', default=SQL_INIT_FILE, help='название SQL-файла')
@click.option('--db-name', '-db', default=PG_DB_NAME, help='имя базы данных')
def db_init(sql_file, db_name):
    """Инициализация новой БД"""
    if db_exists(db_name):
        res = click.prompt(f"Эта процедура полностью удалит базу данных '{db_name}' и создаст новую. Вы согласны? [(д)а/(н)ет] >> ").lower()
        if res in {'да', 'д', 'yes', 'y'}:
            click.echo('Удаляем старую БД, создаем и заполняем новую')
            db_delete(db_name)
            db_create(db_name)
            db_fill(sql_file, db_name)
        else:
            click.echo('Отмена инициализации БД')
    else:
        click.echo('Создаем новую БД и заполняем ее данными')
        db_create(db_name)
        db_fill(sql_file, db_name)


class PGCursor:
    """Курсор работы с Postgres"""
    def __init__(self, connection=None):
        self.connection = connection or connect_db()

    def __enter__(self):
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self.cursor

    def __exit__(self, ext_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if isinstance(exc_value, Exception):
            self.connection.rollback()
        else:
            self.connection.commit()


if __name__ == '__main__':
    # pg_cursor = PGCursor()
    # print(pg_cursor.connection)
    # with pg_cursor as pg:
    #     print(pg)
    #     # rows = pg.execute("""INSERT INTO guiuser ("Login", "Password") VALUES ('user1', 'passwd')""")
    #     # print(rows)
    #     # for row in rows:
    #     #     print(row)

    # print('--- DB exists' + '-'*50)
    # db = 'postgis_31_sample'
    # # db = 'python_db'
    # # pg.execute("""SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{}'""".format(db))
    # # exists = pg.fetchone()
    # # print(exists)
    # print(db_exists(db))
    # print(db_exists('python_db'))
    # print(db_exists('postgres'))

    # # print('--- DB create' + '-'*50)
    # # db_create('python_db')
    # # db_delete('python_db')

    # print('--- DB init' + '-'*50)
    # db_init('python_db')
    db_init()
    # main()