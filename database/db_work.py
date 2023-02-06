from database.db_context_manager import DBConnection
from typing import Tuple, List


def select(database: dict, sql: str) -> Tuple[Tuple, List[str]]:
    """
    Выполняет запрос (SELECT) к БД с указанным конфигом и запросом.
    Args:
        database: dict - Конфиг для подключения к БД.
        sql: str - SQL-запрос.
    Return:
        Кортеж с результатом запроса и описанеим колонок запроса.
    """
    result = tuple()
    schema = []
    with DBConnection(database) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        cursor.execute(sql)
        schema = [column[0] for column in cursor.description]
        result = cursor.fetchall()
    return result, schema


def select_dict(database: dict, sql:str):
    with DBConnection(database) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        cursor.execute(sql)
        result = []
        schema = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            result.append(dict(zip(schema, row)))
    return result


def input_dict(database: dict, sql: str):
    with DBConnection(database) as cursor:
        if cursor is None:
            raise ValueError('Cursor not found')
        try:
            cursor.execute(sql)
            cursor.connection.commit()
        except Exception as ex:
            print(ex)
            raise ValueError('Problem with sql input :(')
        return


def call_proc(database: dict, proc_name: str, *args):
    with DBConnection(database) as cursor:
        if cursor is None:
            raise ValueError('Курсор не найден')
        param_list = []
        for arg in args:
            print('arg=', arg)
            param_list.append(arg)
        print('param_list=', param_list)
        res = cursor.callproc(proc_name, param_list)
    return res
