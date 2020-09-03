import os

import click
import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_database():
    DATABASE_URL = 'postgres://nbvzbasspoitxt:56f71a290346854ee5600d1346a8b234134a5e9498df0fa8d25663b9f12aeaf8@ec2-54-235-192-146.compute-1.amazonaws.com:5432/da8enrbnct70fm'
    if 'database' not in g:
        g.database = psycopg2.connect(DATABASE_URL, sslmode='require')
    # db_name = "ats_db"
    # user_name = "postgres"
    # password = "hajer1991_POSTGRESQL"
    #
    # if 'database' not in g:
    #     g.database = psycopg2.connect(user=user_name, password=password, dbname=db_name)
    return g.database


def close_database(e=None):
    database = g.pop('db', None)

    if database is not None:
        database.close()


def init_database():
    from app.database.operations import insert
    database = get_database()
    cursor = database.cursor()
    with current_app.open_resource('database/scheme.sql') as f:
        cursor.execute(f.read().decode('utf8'))

    insert("Admin", ["username", "password"],
           ('admin', generate_password_hash('admin')))

    expressions = ['ملف رقم', 'إن المحكمة العليا', 'وعليه فإن المحكمة العليا', 'فلهذه الأسباب', 'بذا صدر القرار']
    for e in expressions:
        insert("Separator", ["expression"], (e,))
    close_database()


@click.command('init-database')
@with_appcontext
def init_db_command():
    init_database()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_database)
    app.cli.add_command(init_db_command)
