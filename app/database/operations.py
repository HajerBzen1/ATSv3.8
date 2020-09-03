import psycopg2

from app.database import get_database, close_database


def insert(table: str, columns: list, values: tuple):
    """
    INSERT INTO table (col1, ...) VALUES (%s, ...)
    :param table: string
    :param columns: list
    :param values:tuple (value1, ...)
    :return:
    """
    database = get_database()
    id_ = None
    try:
        cursor = database.cursor()
        query = "INSERT INTO " + table + " (" + ", ".join(columns) + ") VALUES (" + "%s, " * (len(columns) - 1) + "%s)"
        cursor.execute(query, values)
        database.commit()
        cursor.close()
        id_ = select(table, ['id'], ordered_by='id DESC', row_count=1)[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print('While inserting ', error)
        database.rollback()
    finally:
        close_database()
        return id_


def update(table: str, columns: list, values: tuple, where_columns: list = None, where_values: tuple = None):
    """
    UPDATE table SET col1 = %s, ... WHERE col2 = %s, ...
    :param table: string
    :param columns: list
    :param values:tuple (value1, ...)
    :param where_columns: list
    :param where_values: tuple
    :return:
    """
    database = get_database()
    try:
        cursor = database.cursor()
        query = "UPDATE " + table + " SET " + ", ".join([str(c) + "=%s" for c in columns])
        if where_columns and where_values:
            query += " WHERE " + ", ".join([str(w) + "=%s" for w in where_columns])
            cursor.execute(query, values + where_values)
        else:
            cursor.execute(query, values)
        database.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print('While updating ', error)
        database.rollback()
    finally:
        close_database()
        return


def delete(table: str, where_columns: list = None, where_values: tuple = None):
    """
    DELETE  FROM  table WHERE col1 = %s, ...
    :param table: string
    :param where_columns: list
    :param where_values: tuple
    :return:
    """
    database = get_database()
    try:
        cursor = database.cursor()
        query = "DELETE FROM " + table
        if where_columns and where_values:
            query += " WHERE " + ", ".join([str(w) + "=%s" for w in where_columns])
            cursor.execute(query, where_values)
        else:
            cursor.execute(query)
        database.commit()
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print('While deleting ', error)
        database.rollback()
    finally:
        close_database()
        return


def select(tables: str, columns, where_condition: str = None, values: tuple = None, ordered_by: str = None,
           row_count: int = None):
    """
    SELECT col1, col2, ... FROM table1, table2 JOIN table3 ON id2 = id3
    WHERE col1 = %s, ... ORDER BY col1, ...
    :param tables:string
    :param columns:list or '*'
    :param where_condition:string
    :param values:tuple
    :param ordered_by:string
    :param row_count:integer
    :return list
    """
    query = "SELECT " + ", ".join(columns) + " FROM " + tables
    database = get_database()
    result = None
    try:
        cursor = database.cursor()
        if where_condition and values:
            query += " WHERE " + where_condition
        if ordered_by:
            query += " ORDER BY " + ordered_by
        if where_condition and values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        if row_count:
            if row_count == 1:
                result = cursor.fetchone()
            else:
                result = cursor.fetchmany(row_count)
        else:
            result = cursor.fetchall()
    except (Exception, psycopg2.DatabaseError) as error:
        print('While selecting ', error)
        database.rollback()
    finally:
        close_database()
        return result
