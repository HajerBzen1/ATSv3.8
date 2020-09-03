import os

import click
import psycopg2
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_database():
    DATABASE_URL = 'postgres://qesfzxagnordrm:cd4f2f35d6ba450110994cbba6a3b1b65ad3e60469863a219c4c5ee73a78c2ef@ec2-34-200-15-192.compute-1.amazonaws.com:5432/das4a3akik1cvg'
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
